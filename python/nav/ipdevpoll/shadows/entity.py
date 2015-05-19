#
# Copyright (C) 2015 UNINETT
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.  You should have received a copy of the GNU General Public License
# along with NAV. If not, see <http://www.gnu.org/licenses/>.
#
"""NetboxEntity shadow and manager classes for ipdevpoll"""

from __future__ import absolute_import
from collections import defaultdict
from datetime import datetime
from nav.toposort import build_graph, topological_sort

from nav.ipdevpoll.storage import Shadow, DefaultManager
from nav.models import manage
from nav.models.event import EventQueue as Event
from .netbox import Netbox

import networkx as nx
from networkx.algorithms.traversal.depth_first_search import dfs_tree as subtree


class EntityManager(DefaultManager):
    """A manager class for NetboxEntity objects"""
    def __init__(self, *args, **kwargs):
        super(EntityManager, self).__init__(*args, **kwargs)
        self.netbox = self.containers.get(None, Netbox)
        self.matched = set()
        self.missing = set()
        self.existing = set()

    def prepare(self):
        # index known entities in various ways, but only bother to index things
        # that are unique
        index = EntityIndex(manage.NetboxEntity.objects.filter(
            netbox__id=self.netbox.id).select_related('device'))

        matches = ((ent, index.match(ent)) for ent in self.get_managed())
        for collected, model in matches:
            if model:
                collected.set_existing_model(model)
                self.matched.add(model)

        self.existing = index.entities
        self.missing = self.existing.difference(self.matched)

    def cleanup(self):
        if self.missing:
            w_serial = sum(int(m.device is not None) for m in self.missing)
            self._logger.info("%d entities have disappeared, %d of which have "
                              "known serial numbers",
                              len(self.missing), w_serial)

            to_purge = self.get_purge_list()
            to_set_missing = self.missing.difference(to_purge)
            self._logger.info("marking %d entities as missing, purging %d",
                              len(to_set_missing), len(to_purge))

            manage.NetboxEntity.objects.filter(
                id__in=[e.id for e in to_purge]).delete()
            manage.NetboxEntity.objects.filter(
                id__in=[e.id for e in to_set_missing],
                gone_since__isnull=True,
            ).update(gone_since=datetime.now())

            if to_set_missing:
                self._verify_stack_degradation(to_set_missing)

    def get_purge_list(self):
        """Returns a  list of entitites that should be purged from the db"""
        graph = self._build_dependency_graph()
        to_purge = set(self.missing)
        missing = (miss for miss in self.missing
                   if miss.device is not None)
        for miss in missing:
            if miss not in to_purge:
                continue
            sub = subtree(graph, miss)
            to_purge.difference_update(sub.nodes())
        return to_purge

    def _build_dependency_graph(self):
        self._logger.debug("building dependency graph")
        by_id = {entity.id: entity for entity in self.existing}
        graph = nx.DiGraph()

        for entity in self.existing:
            if entity.contained_in_id in by_id:
                parent = by_id[entity.contained_in_id]
                graph.add_edge(parent, entity)

        return graph

    def _verify_stack_degradation(self, missing):
        chassis_count = sum(e.physical_class == e.CLASS_CHASSIS
                            for e in self.existing)
        if chassis_count < 2:
            # we only care about multi-chassis set-ups
            return

        chassis = [m for m in missing
                   if m.physical_class == manage.NetboxEntity.CLASS_CHASSIS]
        if not chassis:
            return
        else:
            self._logger.warning("%d of %d chassis is missing: %s",
                                 len(chassis), chassis_count,
                                 ", ".join(c.name for c in chassis))
        for chass in chassis:
            _dispatch_down_event(chass)

    def get_managed(self):
        """
        Returns managed containers in topological sort order; the point being
        that containers can be inserted into the database in the returned
        order without raising integrity errors.
        """
        managed = super(EntityManager, self).get_managed()
        graph = build_graph(
            managed,
            lambda ent: [ent.contained_in] if ent.contained_in else [])
        return topological_sort(graph)


def entitykey(ent):
    """
    Returns an identity key for an entity object, based on its source MIB and
    index within that MIB.
    """
    return '%s:%s' % (ent.source, ent.index)


def parententitykey(ent):
    """
    Returns an identity key for an entity object's parent object, based on its
    source MIB and contained_in pointer within that MIB.
    """
    if ent.contained_in:
        return '%s:%s' % (ent.source, ent.contained_in)


class NetboxEntity(Shadow):
    """A NetboxEntity shadow class"""
    __shadowclass__ = manage.NetboxEntity
    manager = EntityManager

    def __init__(self, *args, **kwargs):
        super(NetboxEntity, self).__init__(*args, **kwargs)
        if 'gone_since' not in kwargs:
            # make sure to reset the gone_since timestamp on created records
            self.gone_since = None

    def __setattr__(self, key, value):
        if key == 'index' and value is not None:
            value = unicode(value)
        if key == 'contained_in' and value == 0:
            value = None
        super(NetboxEntity, self).__setattr__(key, value)

    def save(self, containers):
        self._check_for_resolved_chassis_outage()
        super(NetboxEntity, self).save(containers)

    def _check_for_resolved_chassis_outage(self):
        if self.physical_class != manage.NetboxEntity.CLASS_CHASSIS:
            return
        entity = getattr(self, '_cached_existing_model', None)
        if entity and entity.gone_since is not None and self.gone_since is None:
            self._logger.info("%s is back up", entity)
            _dispatch_up_event(entity)

    @classmethod
    def get_chassis_entities(cls, containers):
        """Returns a list of chassis entities in containers

        :type containers: nav.ipdevpoll.storage.ContainerRepository
        """
        if cls in containers:
            entities = containers[cls].itervalues()
            return [e for e in entities
                    if e.physical_class == manage.NetboxEntity.CLASS_CHASSIS]
        else:
            return []


class EntityIndex(object):
    """
    Given a sequence of of nav.models.manage.NetboxEntity objects, indexes them
    in various ways applicable for matching them against collected entities.
    """
    def __init__(self, entities):
        self.entities = set(entities)
        self.by_id = self.index_by_id()
        self.by_name = self.index_by_name()
        self.by_serial = self.index_by_serial()

    def match(self, entity):
        """
        Attempts to match entity against one of the indexed
        nav.models.manage.NetboxEntity objects.

        :param entity: The collected entity to find a match for
        :type entiy: NetboxEntity
        :return: A Django model object, if a match was found, otherwise None.
        :rtype: nav.models.manage.NetboxEntity
        """
        match = None
        if entity.device and entity.device.serial:
            match = self.by_serial.get((entity.source, entity.device.serial))
        if not match:
            match = self.by_name.get((entity.source, entity.name))
        if not match:
            match = self.by_id.get(entitykey(entity))
        return match

    def index_by_id(self):
        """
        Builds and returns a dict indexing contained entities by their
        'entitykey'
        """
        return {entitykey(e): e for e in self.entities}

    def index_by_serial(self):
        """
        Builds and returns a dict indexing contained entities by their unique
        serial numbers, if they have one.
        """
        by_serial = defaultdict(list)
        for ent in self.entities:
            if ent.device and ent.device.serial:
                by_serial[(ent.source, ent.device.serial)].append(ent)
        by_serial = {k: v[0] for k, v in by_serial.iteritems() if len(v) == 1}
        return by_serial

    def index_by_name(self):
        """
        Builds and returns a dict indexing contained entities by their unique
        entity names, if they have one.
        """
        by_name = defaultdict(list)
        for ent in self.entities:
            if ent.name:
                by_name[(ent.source, ent.name)].append(ent)
        by_name = {k: v[0] for k, v in by_name.iteritems() if len(v) == 1}
        return by_name


##
## Event dispatch functions
##


def _dispatch_down_event(django_entity):
    event = _make_chassisstate_event(django_entity)
    event.state = event.STATE_START
    event.varmap = {'alerttype': 'chassisDown'}
    event.save()


def _dispatch_up_event(django_entity):
    event = _make_chassisstate_event(django_entity)
    event.state = event.STATE_END
    event.varmap = {'alerttype': 'chassisUp'}
    event.save()


def _make_chassisstate_event(django_entity):
    event = Event()
    event.source_id = 'ipdevpoll'
    event.target_id = 'eventEngine'
    event.device = django_entity.device
    event.netbox = django_entity.netbox
    event.subid = unicode(django_entity.id)
    event.event_type_id = 'chassisState'
    return event
