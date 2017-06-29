from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated
from dry_rest_permissions.generics import DRYPermissions
from dry_rest_permissions.generics import DRYPermissionFiltersBase
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import list_route
from .models import Alerts
from .serializers import AlertsSerializer


class AlertsFilterBackend(DRYPermissionFiltersBase):
    """
    Filters the users to ensure users are now shown to other users who
    shouldn't see them.
    """

    def filter_list_queryset(self, request, queryset, view):

        if request.user.is_anonymous():
            # Return nothing if the user isn't authed
            raise NotAuthenticated()

        return queryset


class AlertsViewSet(viewsets.ModelViewSet):
    """
    Override the various list and detail views to ensure that this endpoint
    is being filtered by an organization and the user making the request is
    an admin of the specific organization being filtered.
    """

    """
    Override the list view for now to filter users down by org.

    TODO:
    -- Figure out a better way to do this.
    -- Require an organization filter to exist. There is no reason people
        should be attempting to view all the users.
    """
    def list(self, request, *args, **kwargs):
        if "alerts" in request._request.GET:
            # = request._request.GET['alerts']
            alert = Alerts.obects.all()
            serializer = AlertsSerializer(alert, many=True)
            return Response(serializer.data)
        else:
            return super(AlertsViewSet, self).list(self, request, *args, **kwargs)

    @list_route(methods=['GET'])
    def current(self, request):
        return Response(AlertsSerializer(request.user).data)

    permission_classes = (DRYPermissions, )
    serializer_class = AlertsSerializer
    queryset = Alerts.objects.all()
    filter_backends = (AlertsFilterBackend, DjangoFilterBackend)
    lookup_field = "message"
