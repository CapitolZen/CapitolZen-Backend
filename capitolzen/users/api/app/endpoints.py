from base64 import b64decode
from json import loads
from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissionFiltersBase
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import NotAuthenticated, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from capitolzen.organizations.models import Organization
from capitolzen.users.api.app.serializers import UserSerializer
from capitolzen.organizations.api.app.serializers import OrganizationSerializer
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

    """

    @list_route(methods=['GET'])
    def current(self, request):
        return Response(UserSerializer(request.user).data)

    @list_route(methods=['post'])
    def register(self, request):

        #
        # We prepare both the organization and user models
        # before saving either so that errors are raised prior
        # to anything being created.

        user_serializer = UserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)

        orgData = {
            'name': request.data['organizationName']
        }

        organization_serializer = OrganizationSerializer(data=orgData)
        organization_serializer.is_valid(raise_exception=True)

        #
        # Make the user first
        user_serializer.save()
        user = user_serializer.instance
        user.set_password(request.data['password'])
        user.save()

        #
        # Do organization things
        organization_serializer.save()
        organization = organization_serializer.instance
        organization.add_user(user)
        return Response({"status": status.HTTP_200_OK})

    @detail_route(methods=['POST'])
    def change_password(self, request, id=None):
        """
        Change Password for an already authenticated user.
        :param request:
        :param pk:
        :return:
        """
        user = self.get_object()
        if not user.check_password(request.data.get('current_password')):
            raise ValidationError(detail="Current password is not correct")

        if request.data.get('password') != request.data.get('confirm_password'):
            raise ValidationError(detail="Password and Confirm Password should be the same")

        from pprint import pprint
        pprint(request.data)

        return Response({"status": status.HTTP_200_OK})

    queryset = User.objects.all()
    permission_classes = (DRYPermissions, )
    serializer_class = UserSerializer
    filter_backends = (UserFilterBackend, DjangoFilterBackend)
    lookup_field = "id"


class PasswordResetViewSet(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        params = request.GET
        email = params.get("email", False)
        if not email:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid request"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=params.get('email', False))
            user.reset_password()
        except Exception:
            pass
        return Response({"status": status.HTTP_200_OK, "message": "password reset email sent"})

    def post(self, request):
        params = loads(request.body)
        password = params.get("password", False)
        token = params.get("hash", False)
        if not token or not password:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid request"},
                            status=status.HTTP_400_BAD_REQUEST)

        decoded = b64decode(token)
        decoded = decoded.decode('utf-8')
        parts = decoded.split('|')
        try:
            user = User.objects.get(id=parts[2])
            valid = user.compare_reset_hash(token)
            if not valid:
                return Response({"status": status.HTTP_403_FORBIDDEN, "message": "Invalid token"},
                                status=status.HTTP_403_FORBIDDEN)
            user.set_password(password)
            user.save()
            return Response({"status": status.HTTP_200_OK, "email": user.username, "message": "password reset"},
                            status=status.HTTP_200_OK)

        except Exception:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid request"},
                            status=status.HTTP_400_BAD_REQUEST)

