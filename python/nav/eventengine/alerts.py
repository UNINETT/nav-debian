#
# Copyright (C) 2012 UNINETT
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
"""Alert generator functionality for the eventEngine"""
import datetime
import os

from nav.models.event import AlertQueue as Alert, EventQueue as Event, AlertType
from nav.models.event import AlertHistory

from django.template import loader, Context

from nav import buildconf

ALERT_TEMPLATE_DIR = os.path.join(buildconf.sysconfdir, 'alertmsg')
INFINITY = datetime.datetime.max

class AlertGenerator(dict):
    def __init__(self, event):
        super(AlertGenerator, self).__init__()
        self.event = event

        self.source = event.source
        self.device = event.device
        self.netbox = event.netbox
        self.subid = event.subid
        self.time = event.time
        self.event_type = event.event_type
        self.state = event.state
        self.value = event.value
        self.severity = event.severity

        self.update(event.varmap)
        self.history_vars = {}

        if 'alert_type' in self:
            self.alert_type = self['alert_type']
            del self['alert_type']
        else:
            self.alert_type = None

    def make_alert(self):
        """Generates an alert object based on the current attributes"""
        attrs = {}
        for attr in ('source', 'device', 'netbox', 'subid', 'time',
                     'event_type', 'state', 'value', 'severity'):
            attrs[attr] = getattr(self, attr)
        alert = Alert(**attrs)
        alert.alert_type = self.get_alert_type()
        alert.varmap = self
        return alert

    def make_alert_history(self):
        """Generates an alert history object based on the current attributes"""
        if self.state == Event.STATE_END:
            return self._resolve_alert_history()

        attrs = dict(
            start_time=self.time,
            end_time=INFINITY if self.state == Event.STATE_START
            else None)
        for attr in ('source', 'device', 'netbox', 'subid', 'event_type',
                     'value', 'severity'):
            attrs[attr] = getattr(self, attr)
        alert = AlertHistory(**attrs)
        alert.alert_type = self.get_alert_type()
        self._update_history_vars(alert)
        return alert

    def _resolve_alert_history(self):
        alert = self._find_existing_alert_history()
        if alert:
            alert.end_time = self.event.time
            self._update_history_vars(alert)
        return alert

    def _update_history_vars(self, alert):
        if self.history_vars:
            vars = alert.varmap
            vars[self.state] = self.history_vars
            alert.varmap = vars

    def _find_existing_alert_history(self):
        unresolved = get_unresolved_alerts_map()
        key = self.event.get_key()
        return unresolved.get(key, None)

    def post(self):
        """Generates and posts the necessary alert objects to the database"""
        history = self.post_alert_history()
        self.post_alert(history)

    def post_alert(self, history=None):
        """Generates and posts an alert on the alert queue only"""
        alert = self.make_alert()
        alert.history = history
        alert.save()
        return alert

    def post_alert_history(self):
        """Generates and posts an alert history record only"""
        history = self.make_alert_history()
        if history:
            history.save()
        return history

    def is_event_duplicate(self):
        """Returns True if the represented event seems to duplicate an
        existing unresolved alert.

        """
        unresolved = get_unresolved_alerts_map()
        return (self.event.state == Event.STATE_START
                and self.event.get_key() in unresolved)

    def get_alert_type(self):
        if not self.alert_type:
            return

        try:
            return AlertType.objects.get(name=self.alert_type)
        except AlertType.DoesNotExist:
            return

def get_unresolved_alerts_map():
    """Returns a dictionary of unresolved AlertHistory entries"""
    unresolved = AlertHistory.objects.filter(end_time__gte=INFINITY)
    return dict((alert.get_key(), alert) for alert in unresolved)

###
### Alert message template processing
###

def _ensure_alert_templates_are_available():
    from django.conf import settings
    if ALERT_TEMPLATE_DIR not in settings.TEMPLATE_DIRS:
        settings.TEMPLATE_DIRS += (ALERT_TEMPLATE_DIR,)

def render_template(alert, msgtype=None, language=None):
    """Renders an alert message template based on the parameters of `alert`.

    :param alert: An :py:class:AlertGenerator object representing the alert
    :param msgtype: The alert medium; one of ['email', 'sms', 'jabber']
    :param language: The language to render the template for.
    :return: A unicode string.
    """
    _ensure_alert_templates_are_available()
    names_to_try = _get_list_of_template_names(alert.event_type,
                                               alert.alert_type, msgtype)
    template = loader.select_template(names_to_try)
    context = Context(dict(alert))
    context.update(vars(alert))
    context.update(dict(msgtype=msgtype, language=language))
    return template.render(context)

def _get_list_of_template_names(event_type, alert_type, msgtype=None,
                                language="en"):
    base_names = [
        "{event_type}/{alert_type}",
        "{event_type}-{alert_type}",
        "{event_type}/default",
        "{event_type}-default",
        "default",
        ]
    if msgtype:
        base_names = [
            "{event_type}/{alert_type}-{msgtype}",
            "{event_type}-{alert_type}-{msgtype}",
            ] + base_names
    names_to_try = ([n + "." + language + ".txt" for n in base_names] +
                    [n + ".txt" for n in base_names])
    return [n.format(**locals()) for n in names_to_try]
