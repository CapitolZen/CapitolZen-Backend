from json import loads
from django.db.models import Q

from dry_rest_permissions.generics import (
    DRYPermissions, DRYPermissionFiltersBase
)

from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters

from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated, NotFound
from rest_framework import mixins

from capitolzen.meta.clients import DocManager
from capitolzen.users.models import User
from capitolzen.organizations.models import (
    Organization, OrganizationInvite, File
)
from capitolzen.organizations.api.app.serializers import (
    OrganizationSerializer, OrganizationInviteSerializer, FileSerializer
)


class OrganizationFilter(filters.FilterSet):
    class Meta:
        model = Organization
        ordering = ['name']
        fields = {
            'id': ['exact'],
            'created': ['lt', 'gt'],
            'modified': ['lt', 'gt'],
            'name': ['icontains'],
        }


class OrganizationFilterBackend(DRYPermissionFiltersBase):
    """

    """

    def filter_list_queryset(self, request, queryset, view):
        """
        Limits all list requests to only show orgs that the user is part of.
        """
        if request.user.is_authenticated():
            return queryset.filter(users=request.user)
        else:
            if not request.GET.get('email'):
                raise NotAuthenticated()

            if not request.GET.get('id'):
                raise NotAuthenticated()

            # id and email filters are handled automatically via DjangoFilter
            email = request.GET.get('email')
            return queryset.filter(owner__organization_user__user__email=email)


class OrganizationViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):

    serializer_class = OrganizationSerializer
    permission_classes = (DRYPermissions,)
    queryset = Organization.objects.all()
    filter_backends = (OrganizationFilterBackend, DjangoFilterBackend)
    filter_class = OrganizationFilter

    @detail_route(methods=['POST'])
    def asset_upload(self, request, pk):
        organization = self.get_object()
        c = DocManager(org_instance=organization)

        data = loads(request.body)

        acl = data.get('acl', False)
        group = data.get('group_id', False)
        params = c.upload_asset(file=data['file_name'], group_id=group, acl=acl)

        return Response({"status": status.HTTP_200_OK, "params": params})

    @list_route(methods=['get'])
    def current(self, request):
        org = Organization.objects.filter(users=request.user).last()
        serializer = OrganizationSerializer(org)

        return Response(serializer.data)


class InviteFilter(filters.FilterSet):
    class Meta:
        model = OrganizationInvite

        fields = {
            'id': ['exact'],
            'created': ['lt', 'gt'],
            'modified': ['lt', 'gt'],
            'organization': ['exact'],
            'status': ['exact'],
            'email': ['exact'],
        }


class OrganizationInviteFilterBackend(DRYPermissionFiltersBase):
    def _get_org_by_consumer_id(self, consumer_id):
        return Organization.objects.get(consumer_id=consumer_id)

    def filter_list_queryset(self, request, queryset, view):
        """
        Limits all list requests to only show orgs that the user is part of.
        """
        if request.user.is_authenticated():
            return queryset.filter(Q(organization__users=request.user))
        else:
            if not request.GET.get('email'):
                raise NotFound()

            if not request.GET.get('id'):
                raise NotFound()

            # id and email filters are handled automatically via DjangoFilter
            return queryset.filter(status="unclaimed")


class OrganizationInviteViewSet(viewsets.ModelViewSet):
    permission_classes = (DRYPermissions,)
    serializer_class = OrganizationInviteSerializer
    queryset = OrganizationInvite.objects.all().order_by('created')
    filter_backends = (OrganizationInviteFilterBackend, DjangoFilterBackend)
    filter_class = InviteFilter

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.status != "unclaimed":
            response = {'detail': "Can only delete unclaimed invites"}
            return Response(data=response,
                            status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(obj)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        user = instance.user
        if user:
            user.delete()  # delete cascades
        else:
            instance.delete()

    def perform_create(self, serializer):
        """
        Send email and create user for the invite.
        """

        instance = serializer.save(status="unclaimed")
        user = User.objects.create(username=instance.email)
        instance.user = user

        # Double save is a little rough here...
        instance.save()
        instance.send_user_invite()

    @detail_route(methods=['post'], permission_classes=(AllowAny,))
    def claim(self, request, pk=None):
        if request.user and request.user.is_authenticated:
            return Response({"detail": "Cannot claim invite"},
                            status=status.HTTP_401_UNAUTHORIZED)

        invite = self.get_object()

        if invite.status != "unclaimed":
            return Response({"detail": "Cannot claim invite"},
                            status=status.HTTP_401_UNAUTHORIZED)

        # Setup the user's password.
        password = request.data.get('password')
        invite.user.update_provider({'password': password})

        # Add user to organization.
        organization_role = invite.meta_data.get('organization_role', "Member")

        if organization_role == "Admin":
            is_admin = True
        else:
            is_admin = False

        invite.organization.add_user(invite.user, is_admin=is_admin)
        invite.status = "claimed"
        invite.save()

        return Response({"detail": "Invite claimed"},
                        status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def actions(self, request, pk=None):
        invite = self.get_object()
        if invite.status != 'unclaimed':
            return Response({"status_code": status.HTTP_400_BAD_REQUEST,
                             "detail":
                                 "You may only take actions on pending invites"},
                            status=status.HTTP_400_BAD_REQUEST)

        action = request.data.get('actions', False)

        if not action:
            return Response({"detail": "Please provide an action."},
                            status=status.HTTP_400_BAD_REQUEST)

        if action == 'resend':
            invite.send_user_invite()
            return Response({"status_code": status.HTTP_200_OK,
                             "detail": "Invite resent"})

        return Response({"status_code": status.HTTP_400_BAD_REQUEST,
                         "detail": "Invalid request"})


class FileFilter(filters.FilterSet):
    class Meta:
        model = File
        ordering = ['name']
        fields = {
            'id': ['exact'],
            'created': ['lt', 'gt'],
            'modified': ['lt', 'gt'],
            'name': ['icontains'],
        }


class FileViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return File.objects.filter(organization__users=self.request.user)

    filter_class = FileFilter
    filter_backends = (DjangoFilterBackend, )
    permission_classes = (DRYPermissions, )
    serializer_class = FileSerializer
