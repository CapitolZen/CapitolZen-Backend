from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated
from dry_rest_permissions.generics import DRYPermissions
from dry_rest_permissions.generics import DRYPermissionFiltersBase
from django_filters.rest_framework import DjangoFilterBackend

from capitolzen.organizations.models import Organization

from .models import User
from .serializers import UserSerializer


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


    permission_classes = (DRYPermissions, )
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_backends = (UserFilterBackend, DjangoFilterBackend)
    lookup_field = "username"