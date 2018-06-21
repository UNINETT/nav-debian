#
# Copyright (C) 2008-2009 Uninett AS
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 2 as published by the Free
# Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.  You should have received a copy of the GNU General Public License
# along with NAV. If not, see <http://www.gnu.org/licenses/>.
#
"""Django URL configuration for devicehistory."""

from django.conf.urls import url, patterns

from nav.web.devicehistory.views import (devicehistory_search,
                                         devicehistory_view, error_form,
                                         register_error, delete_module,
                                         do_delete_module)

# The patterns are relative to the base URL of the subsystem
urlpatterns = patterns('',
    url(r'^$', devicehistory_search, name='devicehistory-search'),

    url(r'^history/$', devicehistory_view, name='devicehistory-view'),
    url(r'^history/\?netbox=(?P<netbox_id>\d+)$', devicehistory_view,
        name='devicehistory-view-netbox'),
    url(r'^history/\?room=(?P<room_id>.+)$', devicehistory_view,
        name='devicehistory-view-room'),
    url(r'^history/\?loc=(?P<location_id>.+)$', devicehistory_view,
        name='devicehistory-view-location'),

    url(r'^registererror/$', error_form,
        name='devicehistory-registererror'),
    url(r'^do_registererror/$', register_error,
        name='devicehistory-do-registererror'),

    url(r'^delete_module/$', delete_module,
        name='devicehistory-module'),
    url(r'^do_delete_module/$', do_delete_module,
        name='devicehistory-do_delete_module'),
)
