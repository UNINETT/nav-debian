#
# Copyright (C) 2011 Uninett AS
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
"""SeedDB Django URL config"""

from django.conf.urls import patterns, url

from nav.web.maintenance.views import active, planned, historic, calendar
from nav.web.maintenance.views import view, cancel, edit, redirect_to_calendar
from nav.web.maintenance.views import add_box_to_maintenance

dummy = lambda *args, **kwargs: None

urlpatterns = patterns('',
    url(r'^$', redirect_to_calendar),
    url(r'^calendar/$', calendar,
        name='maintenance'),
    url(r'^calendar/$', calendar,
        name='maintenance-calendar'),
    url(r'^calendar/\?year=(?P<year>\d{4})&month=(?P<month>\d{1,2})$', calendar,
        name='maintenance-calendar'),
    url(r'^active/$', active,
        name='maintenance-active'),
    url(r'^planned/$', planned,
        name='maintenance-planned'),
    url(r'^historic/$', historic,
        name='maintenance-historic'),
    url(r'^new/$', edit,
        name='maintenance-new'),
    url(r'^new/(?P<start_time>\d{4}-\d{2}-\d{2})/$', edit,
        name='maintenance-new-date'),
    url(r'^edit/(?P<task_id>\d+)/$', edit,
        name='maintenance-edit'),
    url(r'^view/(?P<task_id>\d+)/$', view,
        name='maintenance-view'),
    url(r'^cancel/(?P<task_id>\d+)/$', cancel,
        name='maintenance-cancel'),
    url(r'^addnetbox/$', add_box_to_maintenance,
        name='maintenance-add-netbox'),

    url(r'^new\?netbox=(?P<netbox_id>\d+)$', dummy,
        name='maintenance-new-netbox'),
    url(r'^new\?service=(?P<service_id>\d+)$', dummy,
        name='maintenance-new-service'),
    url(r'^new\?room=(?P<room_id>.+)$', dummy,
        name='maintenance-new-room'),
)
