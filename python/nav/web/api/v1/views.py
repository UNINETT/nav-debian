# Copyright (C) 2013 UNINETT AS
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
# pylint: disable=R0903, R0901, R0904
"""Views for the NAV API"""

from IPy import IP
from django.http import HttpResponse
from django.db.models import Q
from datetime import datetime, timedelta
import iso8601

from provider.utils import long_token
from rest_framework import status, filters, viewsets
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.reverse import reverse
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.generics import ListAPIView
from nav.models.api import APIToken
from nav.models import manage, event
from nav.models.fields import INFINITY, UNRESOLVED
from nav.web.servicecheckers import load_checker_classes

from nav.web.api.v1 import serializers, alert_serializers
from .auth import APIPermission, APIAuthentication, NavBaseAuthentication
from .helpers import prefix_collector
from .filter_backends import AlertHistoryFilterBackend
from nav.web.status2 import STATELESS_THRESHOLD

EXPIRE_DELTA = timedelta(days=365)
MINIMUMPREFIXLENGTH = 4


@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def api_root(request):
    """Create api root for informing about possible endpoints"""
    return Response({
        'room': reverse('api:1:room-list', request=request),
        'netbox': reverse('api:1:netbox-list', request=request),
        'interface': reverse('api:1:interface-list', request=request),
        'cam': reverse('api:1:cam-list', request=request),
        'arp': reverse('api:1:arp-list', request=request),
        'alert': reverse('api:1:alerthistory-list', request=request),
        'servicehandler': reverse('api:1:servicehandler-list',
                                  request=request),
        'prefix': reverse('api:1:prefix-list', request=request),
        'vlan': reverse('api:1:vlan-list', request=request),
        'prefix_routed': reverse('api:1:prefix-routed-list', request=request),
        'prefix_usage': reverse('api:1:prefix-usage-list', request=request),
    })


class NAVAPIMixin(APIView):
    """Mixin for providing permissions and renderers"""
    authentication_classes = (NavBaseAuthentication, APIAuthentication)
    permission_classes = (APIPermission,)
    renderer_classes = (JSONRenderer,)
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)


class ServiceHandlerViewSet(NAVAPIMixin, ViewSet):
    """Makes service handlers available from the API"""

    def list(self, _request):
        """Handle list requests"""
        queryset = [self._build_object(c) for c in load_checker_classes()]
        serializer = serializers.ServiceHandlerSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, _request, pk=None):
        """Handle retrieve requests"""
        for checker in load_checker_classes():
            if checker.get_type() == pk:
                serializer = serializers.ServiceHandlerSerializer(
                    self._build_object(checker))
                return Response(serializer.data)

    @staticmethod
    def _build_object(checker):
        return {
            'name': checker.get_type(),
            'ipv6_support': checker.IPV6_SUPPORT,
            'description': checker.DESCRIPTION
        }


class RoomViewSet(NAVAPIMixin, viewsets.ReadOnlyModelViewSet):
    """Makes rooms accessible from api"""
    queryset = manage.Room.objects.all()
    serializer_class = serializers.RoomSerializer
    filter_fields = ('location', 'description')


class NetboxViewSet(NAVAPIMixin, viewsets.ReadOnlyModelViewSet):
    """Makes netboxes accessible from api"""
    queryset = manage.Netbox.objects.all()
    serializer_class = serializers.NetboxSerializer
    filter_fields = ('ip', 'sysname', 'room', 'organization', 'category')
    search_fields = ('sysname', )


class InterfaceViewSet(NAVAPIMixin, viewsets.ReadOnlyModelViewSet):
    """Makes interfaces accessible from api"""
    queryset = manage.Interface.objects.all()
    serializer_class = serializers.InterfaceSerializer
    filter_fields = ('ifname', 'ifindex', 'ifoperstatus', 'netbox', 'trunk',
                     'ifadminstatus', 'iftype', 'baseport')
    search_fields = ('ifalias', 'ifdescr', 'ifname')


class CamViewSet(NAVAPIMixin, viewsets.ReadOnlyModelViewSet):
    """Makes cam accessible from api"""
    serializer_class = serializers.CamSerializer
    filter_fields = ('mac', 'netbox', 'ifindex', 'port')

    def get_queryset(self):
        """Filter on custom parameters"""
        queryset = manage.Cam.objects.all()
        active = self.request.QUERY_PARAMS.get('active', None)
        if active:
            queryset = queryset.filter(end_time=INFINITY)

        return queryset


class ArpViewSet(NAVAPIMixin, viewsets.ReadOnlyModelViewSet):
    """Makes cam accessible from api"""
    serializer_class = serializers.ArpSerializer
    filter_fields = ('ip', 'mac', 'netbox', 'prefix')

    def get_queryset(self):
        """Filter on custom parameters"""
        queryset = manage.Arp.objects.all()
        active = self.request.QUERY_PARAMS.get('active', None)
        if active:
            queryset = queryset.filter(end_time=INFINITY)

        return queryset


class VlanViewSet(NAVAPIMixin, viewsets.ReadOnlyModelViewSet):
    """Makes vlans available from api"""
    queryset = manage.Vlan.objects.all()
    serializer_class = serializers.VlanSerializer
    filter_fields = ['vlan', 'net_type', 'net_ident', 'description',
                     'organization', 'usage']
    search_fields = ['net_ident', 'description']


class PrefixViewSet(NAVAPIMixin, viewsets.ReadOnlyModelViewSet):
    """Makes prefixes available from api"""
    queryset = manage.Prefix.objects.all()
    serializer_class = serializers.PrefixSerializer
    filter_fields = ('vlan', 'net_address', 'vlan__vlan')


class RoutedPrefixList(NAVAPIMixin, ListAPIView):
    """Fetches routed prefixes"""
    _router_categories = ['GSW', 'GW']
    serializer_class = serializers.PrefixSerializer

    def get_queryset(self):
        prefixes = manage.Prefix.objects.filter(
            gwportprefix__interface__netbox__category__in=
            self._router_categories)
        if 'family' in self.request.GET:
            prefixes = prefixes.extra(where=['family(netaddr)=%s'],
                                      params=[self.request.GET.get('family')])

        return prefixes


def get_times(request):
    """Gets start and endtime from request"""
    starttime = request.GET.get('starttime')
    endtime = request.GET.get('endtime')
    if starttime:
        starttime = iso8601.parse_date(starttime)
    if endtime:
        endtime = iso8601.parse_date(endtime)
    return starttime, endtime


class PrefixUsageList(NAVAPIMixin, ListAPIView):
    """Makes prefix usage for all prefixes available"""
    serializer_class = serializers.PrefixUsageSerializer

    def get(self, request, *args, **kwargs):
        """Override get method to verify url parameters"""
        try:
            get_times(request)
        except (ValueError, iso8601.ParseError):
            return Response(
                'start or endtime not formatted correctly. Use iso8601 format',
                status=status.HTTP_400_BAD_REQUEST)
        return super(PrefixUsageList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        """Filter for ip family"""
        if 'scope' in self.request.GET:
            queryset = manage.Prefix.objects.within(
                self.request.GET.get('scope')).order_by('net_address')
        elif 'family' in self.request.GET:
            queryset = manage.Prefix.objects.extra(
                where=['family(netaddr)=%s'],
                params=[self.request.GET.get('family')])
        else:
            queryset = manage.Prefix.objects.all()

        return queryset

    def list(self, request, *args, **kwargs):
        """Delivers a list of usage objects as a response

        The queryset contains prefixes, but we use a custom object for
        representing the usage statistics for the prefix. Thus we need to
        convert the filtered prefixes to the custom object format.

        Also we need to run the prefix collector after paging to avoid
        unnecessary usage calculations
        """
        self.object_list = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(self.object_list)

        starttime, endtime = get_times(self.request)
        prefixes = prefix_collector.fetch_usages([
            p for p in page.object_list
            if IP(p.net_address).len() >= MINIMUMPREFIXLENGTH],
            starttime, endtime)

        if page is not None:
            page.object_list = prefixes
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(prefixes, many=True)

        return Response(serializer.data)



class PrefixUsageDetail(NAVAPIMixin, APIView):
    """Makes prefix usage accessible from api"""

    @staticmethod
    def get(request, prefix):
        """Handles get request for prefix usage"""

        try:
            ip_prefix = IP(prefix)
        except ValueError:
            return Response("Bad prefix", status=status.HTTP_400_BAD_REQUEST)

        if ip_prefix.len() < MINIMUMPREFIXLENGTH:
            return Response("Prefix is too small",
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            starttime, endtime = get_times(request)
        except (ValueError, iso8601.ParseError):
            return Response(
                'start or endtime not formatted correctly. Use iso8601 format',
                status=status.HTTP_400_BAD_REQUEST)

        db_prefix = manage.Prefix.objects.get(net_address=prefix)
        serializer = serializers.PrefixUsageSerializer(
            prefix_collector.fetch_usage(db_prefix, starttime, endtime))

        return Response(serializer.data)


class AlertHistoryViewSet(NAVAPIMixin, viewsets.ReadOnlyModelViewSet):
    """API view for listing AlertHistory entries"""

    filter_backends = (AlertHistoryFilterBackend,)
    queryset = event.AlertHistory.objects.none()
    serializer_class = alert_serializers.AlertHistorySerializer

    def get_queryset(self):
        """Gets an AlertHistory QuerySet"""
        if not self.request.QUERY_PARAMS.get('stateless', False):
            return event.AlertHistory.objects.unresolved().select_related(
                depth=1)
        else:
            return self._get_stateless_queryset()

    def _get_stateless_queryset(self):
        hours = int(self.request.QUERY_PARAMS.get('stateless_threshold',
                                                  STATELESS_THRESHOLD))
        if hours < 1:
            raise ValueError("hours must be at least 1")
        threshold = datetime.now() - timedelta(hours=hours)
        stateless = Q(start_time__gte=threshold) & Q(end_time__isnull=True)
        return event.AlertHistory.objects.filter(
            stateless | UNRESOLVED).select_related(depth=1)


def get_or_create_token(request):
    """Gets an existing token or creates a new one. If the old token has
    expired, create a new one.

    :type request: django.http.HttpRequest
    """
    if request.account.is_admin():
        token, _ = APIToken.objects.get_or_create(
            client=request.account, expires__gte=datetime.now(),
            defaults={'token': long_token(),
                      'expires': datetime.now() + EXPIRE_DELTA})
        return HttpResponse(str(token))
    else:
        return HttpResponse('You must log in to get a token',
                            status=status.HTTP_403_FORBIDDEN)
