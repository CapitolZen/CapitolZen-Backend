from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissionFiltersBase
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response

from capitolzen.organizations.models import Organization
from capitolzen.users.api.app.serializers import UserSerializer
from capitolzen.users.models import User
from capitolzen.users.api.app.serializers import AlertsSerializer
from capitolzen.users.models import Alerts
from rest_framework import status


class UserFilterBackend(DRYPermissionFiltersBase):
    """
    Filters the users to ensure users are now shown to other users who
    shouldn't see them.
    """

    def filter_list_queryset(self, request, queryset, view):

        if request.user.is_anonymous():
            # Return nothing if the user isn't authed
            raise NotAuthenticated()

        return queryset


class UserViewSet(viewsets.ModelViewSet):
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
        if "organization" in request._request.GET:
            organization_id = request._request.GET['organization']
            organization = Organization.objects.get(pk=organization_id)
            users = organization.users.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        else:
            return super(UserViewSet, self).list(self, request, *args, **kwargs)

    @list_route(methods=['GET'])
    def current(self, request):
        return Response(UserSerializer(request.user).data)

    permission_classes = (DRYPermissions, )
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_backends = (UserFilterBackend, DjangoFilterBackend)
    lookup_field = "username"


class AlertsFilterBackend(DRYPermissionFiltersBase):
    def filter_list_queryset(self, request, queryset, view):
        queryset = Alerts.objects.filter(user=request.user)
        return queryset


class AlertsViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user
        return Alerts.objects.filter(user=user)

    @list_route(methods=['GET'])
    def current(self, request):
        return Response(AlertsSerializer(request.user).data)

    @detail_route(methods=['POST'])
    def dismiss(self, request, id):
        alert = Alerts.objects.get(id=id)
        alert.is_read = True
        alert.save()
        return Response(id, status=status.HTTP_200_OK)

    permission_classes = (DRYPermissions, )
    serializer_class = AlertsSerializer
    queryset = Alerts.objects.all()
    filter_backends = (AlertsFilterBackend, DjangoFilterBackend)
    lookup_field = "id"

