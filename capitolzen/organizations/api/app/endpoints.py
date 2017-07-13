from json import loads
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import (DRYPermissions,
                                           DRYPermissionFiltersBase)
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from capitolzen.meta.clients import DocManager
from capitolzen.groups.models import Group
from capitolzen.users.api.app.serializers import UserSerializer
from capitolzen.users.models import User
from capitolzen.organizations.models import (Organization, OrganizationInvite)
from .serializers import (OrganizationSerializer, OrganizationInviteSerializer)


class OrganizationFilterBackend(DRYPermissionFiltersBase):
    """

    """

    def filter_list_queryset(self, request, queryset, view):
        """
        Limits all list requests to only show orgs that the user is part of.
        """

        if request.user.is_anonymous():
            return queryset.filter(pk=0)
        else:
            if request.user.is_superuser:
                # Return all orgs if superuser status
                return queryset
            elif request.user.is_staff:
                # Allow for staff users to use user_is_member filtering.
                if request.GET.get('user_is_member'):
                    return queryset.filter(users=request.user)
                else:
                    return queryset
            else:
                return queryset.filter(users=request.user)
        return queryset


class OrganizationViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        return OrganizationSerializer

    @detail_route(methods=['get'])
    def users(self, request, pk=None):
        organization = self.get_object()
        users = organization.users.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def logo_upload(self):
        organization = self.get_object()
        c = DocManager(org_instance=organization)
        params = c.upload_logo()
        params['acl'] = 'public-read'
        return Response({"status": status.HTTP_200_OK, "params": params})

    @detail_route(methods=['POST'])
    def asset_upload(self, request, pk):
        organization = self.get_object()
        c = DocManager(org_instance=organization)

        data = loads(request.body)

        acl = data.get('acl', False)
        params = c.upload_asset(file=data['file_name'], group_id=data['group_id'], acl=acl)

        return Response({"status": status.HTTP_200_OK, "params": params})

    @list_route(methods=['get'])
    def current(self, request):
        user = User.objects.get(request.user)
        orgs = Organization.objects.filter(user=user)
        serializer = OrganizationSerializer(orgs, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Override the perform_create to add the owner in automatically.
        """
        user = self.request.user
        org = serializer.save()
        org.is_active = True
        org.add_user(user, is_admin=True)
        org.save()
        """
        Create default group
        """
        g = Group.objects.create(
            title="Default Group for %s" % org.name,
            organization=org,
            description="Default group for your account"
        )

        g.save()

    permission_classes = (DRYPermissions, )
    queryset = Organization.objects.all()
    filter_backends = (OrganizationFilterBackend, DjangoFilterBackend)
    filter_fields = ('is_active',)


class OrganizationInviteFilterBackend(DRYPermissionFiltersBase):

    def filter_list_queryset(self, request, queryset, view):
        """
        Limits all list requests to only show orgs that the user is part of.
        """
        if request.user.is_authenticated():
            if request.GET.get('email'):
                return queryset.filter(Q(organization__users=request.user) |
                                       Q(email=request.GET.get('email')))
            else:
                return queryset.filter(Q(organization__users=request.user))

        else:
            return queryset


class OrganizationInviteViewSet(viewsets.ModelViewSet):
    """
    TODO:
    -- We need to cleanup the permissions on this. Right now needs
       to be set to AllowAny so that anon users can retrieve their own invites.
    -- Fixup claim. Should only be able to claim unclaimed invites, send
        back real error responses.

    If the org is owned by staff, the first member to join claims it.
    """

    @detail_route(methods=['post'])
    def claim(self, request, pk=None):
        invite = self.get_object()
        user = request.user
        # Only add if not already in the org
        if user.is_authenticated and not invite.organization.is_member(user):

            # If the organization owner is a staff member it probably
            # means the organization was created by an admin, not self-service.
            """

            if invite.organization.owner.organization_user.user.is_staff:
                old_owner = invite.organization.owner.organization_user
                new_owner = invite.organization.get_or_add_user(user)
                invite.organization.save()
                if old_owner != new_owner:
                    # invite.organization.save()
                    invite.organization.change_owner(new_owner)
                    invite.organization.remove_user(old_owner.user)
            else:
            """
            invite.organization.add_user(user)
            invite.status = "claimed"
            invite.save()
            return Response({"status_code": status.HTTP_200_OK,
                             "detail": "Invite claimed"},
                            status=status.HTTP_200_OK)
        return Response({"status_code": status.HTTP_400_BAD_REQUEST,
                         "detail": "Invalid request"},
                        status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def actions(self, request, pk=None):
        invite = self.get_object()
        # Can't revoke invite that has been accepted for whatever reason
        if invite.status != 'pending':
            return Response({"status_code": status.HTTP_400_BAD_REQUEST,
                             "detail":
                            "You may only take actions on pending invites"})

        if request.data['actions'] == 'revoke':
            invite.status = "revoked"
            invite.save()
            return Response({"status_code": status.HTTP_200_OK,
                             "detail": "Invite revoked"})

        if request.data['actions'] == 'resend':
            invite.send_user_invite()
            return Response({"status_code": status.HTTP_200_OK,
                             "detail": "Invite resent"})

        if request.data['actions'] == 'update':
            invite.email = request.data['email']
            invite.save()
            return Response({"status_code": status.HTTP_200_OK,
                             "detail": "Invite updated"})

        return Response({"status_code": status.HTTP_400_BAD_REQUEST,
                         "detail": "Invalid request"})

    permission_classes = (AllowAny, )
    serializer_class = OrganizationInviteSerializer
    queryset = OrganizationInvite.objects.all()
    filter_backends = (OrganizationInviteFilterBackend, DjangoFilterBackend)
    filter_fields = ('status', 'organization', 'email')
