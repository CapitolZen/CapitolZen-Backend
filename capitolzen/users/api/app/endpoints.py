from django_filters.rest_framework import DjangoFilterBackend

from dry_rest_permissions.generics import DRYPermissionFiltersBase
from dry_rest_permissions.generics import DRYPermissions
from django_filters import rest_framework as filters

from config.viewsets import BasicViewSet

from rest_framework.exceptions import APIException
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import mixins
from rest_framework import status

from common.utils.filters.sets import BaseModelFilterSet

from capitolzen.organizations.models import OrganizationInvite

from capitolzen.users.api.app.serializers import (
    ChangePasswordSerializer,
    RegistrationSerializer, ResetPasswordRequestSerializer,
    ResetPasswordSerializer,
    ChangeUserOrganizationRoleSerializer, ChangeUserStatusSerializer, GuestUserCreateSerializer,
    ActionSerializer, UserSerializer
)

from capitolzen.users.models import User, Action


class UserFilter(filters.FilterSet):
    current = filters.BooleanFilter(
        name="current",
        label="Current",
        method="filter_current"
    )

    guest = filters.CharFilter(
        method="filter_guest"
    )

    def filter_current(self, queryset, name, value):
        if value:
            return queryset.filter(id=self.request.user.id)
        else:
            return queryset

    def filter_guest(self, queryset, name, value):
        return queryset.filter(guest_users_users=value)

    class Meta:
        model = User
        ordering = ['name']
        fields = {}


class UserFilterBackend(DRYPermissionFiltersBase):
    """
    -- Don't show any users to anon
    -- Only show users to users who are in the current organization.
    """

    def filter_list_queryset(self, request, queryset, view):
        if request.user.is_anonymous():
            raise NotAuthenticated()
        if hasattr(request, 'organization') and request.organization:
            qs = queryset.filter(organizations_organization=request.organization)
            if not request.GET.get('guest', None) and not request.GET.get('current', False):
                qs = qs.filter(guest_users_users=None)
            return qs

        if request.user.is_superuser or request.user.is_staff:
            return queryset
        else:
            return queryset.filter(id=request.user.id)


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    Catchall user endpoint.
    """
    queryset = User.objects.all()
    permission_classes = (DRYPermissions,)
    serializer_class = UserSerializer
    filter_backends = (UserFilterBackend, DjangoFilterBackend)
    filter_class = UserFilter
    lookup_field = 'id'

    @detail_route(methods=['POST'])
    def login(self, request, id=None):
        """
        Upon user login, we do a couple of things.

        2) Claim invites.
        :param request:
        :param pk:
        :return:
        """
        self.get_object()

        #
        # Claim invite
        invite_id = request.data.get('invite')
        if invite_id:
            try:
                invite = OrganizationInvite.objects.get(id=invite_id)
            except OrganizationInvite.DoesNotExist:
                raise APIException(detail="Unable to load invite")

            organization_role = \
                invite.meta_data.get('organization_role', "Member")
            is_admin = True if organization_role == "Admin" else False
            invite.organization.add_user(request.user, is_admin=is_admin)
            invite.status = "claimed"
            invite.save()

        return Response(data={'status': 'login'})

    @list_route(methods=['post'],
                serializer_class=RegistrationSerializer,
                permission_classes=(AllowAny,))
    def register(self, request):
        """
        User Registration
        :param request:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if instance:
            return Response({"status": status.HTTP_200_OK})
        else:
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'],
                serializer_class=ResetPasswordRequestSerializer,
                permission_classes=(AllowAny,))
    def reset_password_request(self, request):
        """
        Reset password request
        :param request:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if instance:
            return Response({"status": status.HTTP_200_OK})
        else:
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'],
                serializer_class=ResetPasswordSerializer,
                permission_classes=(AllowAny,))
    def reset_password(self, request):
        """
        Reset Password
        :param request:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        if instance:
            return Response(instance)
        else:
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], serializer_class=ChangePasswordSerializer)
    def change_password(self, request, id=None):
        """
        Change Password for an already authenticated user.
        :param request:
        :param pk:
        :return:
        """
        user = self.get_object()
        data = request.data
        data['user'] = user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if instance:
            return Response({"status": status.HTTP_200_OK})
        else:
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], serializer_class=ChangeUserStatusSerializer)
    def change_status(self, request, id=None):
        """
        Change status of user.
        :param request:
        :param pk:
        :return:
        """
        user = self.get_object()
        data = request.data
        data['user'] = user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if instance:
            return Response({"status": status.HTTP_200_OK})
        else:
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], serializer_class=ChangeUserOrganizationRoleSerializer)
    def change_organization_role(self, request, id=None):
        """
        Change status of user.
        :param request:
        :param pk:
        :return:
        """
        user = self.get_object()
        data = request.data
        data['user'] = user.id
        data['organization'] = request.organization.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if instance:
            return Response({"status": status.HTTP_200_OK})
        else:
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'], serializer_class=GuestUserCreateSerializer)
    def create_guest(self, request, id=None):
        data = request.data
        data['organization'] = request.organization.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        if instance:
            return Response(UserSerializer(instance).data)
        else:
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST)

class ActionFilter(BaseModelFilterSet):
    group = filters.UUIDFilter(
        name='wrapper__group__id',
        lookup_expr='exact',
        label='actions for wrappers of groups',
        help_text='title of group'
    )

    class Meta:
        model = Action
        ordering = ['-priority', ]
        fields = {
            'id': ['exact'],
            'created': ['lt', 'gt'],
            'modified': ['lt', 'gt'],
            'state': ['exact'],
            'priority': ['lt', 'gt', 'exact'],
            'title': ['exact']
        }


class ActionsViewSet(BasicViewSet):

    def get_queryset(self):
        return Action.objects.filter(user=self.request.user)

    filter_class = ActionFilter
    serializer_class = ActionSerializer

    ordering_fields = ('bill__state_id', 'bill__created_at', 'bill__updated_at')
    search_fields = (
        'bill__title',
        'bill__state_id',
        'bill__sponsor__last_name',
        'title'
    )

    @list_route(methods=['get'])
    def stats(self, request):
        if not getattr(request, 'user', False):
            return Response({"message": "INvalid request", "status": status.HTTP_403_FORBIDDEN})
        user = request.user

        queryset = Action.objects.filter(user=user, state='active')

        data = {
            'introduced': queryset.filter(title='bill:introduced').count(),
            'updated': queryset.filter(title='wrapper:updated').count(),
            'total': queryset.count()
        }

        return Response({"status_code": status.HTTP_200_OK, "stats": data})
