from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissionFiltersBase
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from capitolzen.organizations.models import Organization
from capitolzen.users.api.app.serializers import (UserSerializer,
                                                  ChangePasswordSerializer,
                                                  RegistrationSerializer,
                                                  ResetPasswordRequestSerializer,
                                                  ResetPasswordSerializer)
from capitolzen.users.models import User
from rest_framework import status


class UserFilterBackend(DRYPermissionFiltersBase):
    """
    -- Don't show any users to anon
    -- Only show users to users who are in the current organization.
    """

    def filter_list_queryset(self, request, queryset, view):

        if request.user.is_anonymous():
            raise NotAuthenticated()

        current_user_organizations = Organization.objects.for_user(request.user)
        return queryset.filter(organizations_organization=current_user_organizations)


class UserViewSet(viewsets.ModelViewSet):
    """
    Catchall user endpoint.
    """

    @list_route(methods=['GET'])
    def current(self, request):
        """
        Return the currently logged in user.
        :param request:
        :return:
        """
        return Response(UserSerializer(request.user).data)

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

    queryset = User.objects.all()
    permission_classes = (DRYPermissions, )
    serializer_class = UserSerializer
    filter_backends = (UserFilterBackend, DjangoFilterBackend)
    lookup_field = "id"
