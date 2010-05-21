# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 UNINETT AS
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.  You should have received a copy of the GNU General Public
# License along with NAV. If not, see <http://www.gnu.org/licenses/>.
#
"""Implements a MibRetriever for the CISCO-IETF-IP-MIB."""
from twisted.internet import defer

from ip_mib import IpMib

class CiscoIetfIpMib(IpMib):
    """CISCO-IETF-IP-MIB is based on a a draft version of IETF's
    revised IP-MIB (with address type agnostic extensions).  Its
    structure is basically the same, with altered object names and
    ids. 

    We try to avoid code redundancies by inheriting from the IpMib
    MibRetriever implementation, which was written using the revised
    IP-MIB.

    """
    from nav.smidumps.cisco_ietf_ip_mib import MIB as mib

    @classmethod
    def address_index_to_ip(cls, index):
        """Convert a row index from cIpAddressTable to an IP object."""

        entry = cls.nodes['cIpAddressEntry']
        if entry.oid.isaprefix(index):
            # Chop off the entry OID+column prefix
            index = index[(len(entry.oid) + 1):]

        return super(CiscoIetfIpMib, cls).address_index_to_ip(index)

    @classmethod
    def prefix_index_to_ip(cls, index):
        """Convert a row index from cIpAddressPfxTable to an IP object."""

        entry = cls.nodes['cIpAddressPfxEntry']
        if entry.oid.isaprefix(index):
            # Chop off the entry OID+column prefix
            index = index[(len(entry.oid) + 1):]

        return super(CiscoIetfIpMib, cls).prefix_index_to_ip(index)

    @defer.deferredGenerator
    def get_ifindex_ip_mac_mappings(self):
        """Retrieve the layer 3->layer 2 address mappings of this device.

        Return value:
          A set of tuples: set([(ifindex, ip_address, mac_address), ...])
          ifindex will be an integer, ip_address will be an IPy.IP object and
          mac_address will be a string with a colon-separated hex representation
          of a MAC address.

        """
        waiter = defer.waitForDeferred(self._get_ifindex_ip_mac_mappings(
                column='cInetNetToMediaPhysAddress'))
        yield waiter
        mappings = waiter.getResult()

        yield mappings

    @defer.deferredGenerator
    def get_interface_addresses(self):
        """Retrieve the IP addresses and prefixes of interfaces.

        Return value:
          A set of tuples: set([(ifindex, ip_address, prefix_address), ...])
          ifindex will be an integer, ip_address and prefix_address will be
          IPy.IP objects.

        """
        waiter = defer.waitForDeferred(self._get_interface_addresses(
                ifindex_column='cIpAddressIfIndex',
                prefix_column='cIpAddressPrefix',
                prefix_entry='cIpAddressPfxEntry'))
        yield waiter
        addresses = waiter.getResult()

        yield addresses
        
