from django.core.mail import send_mail
from base64 import b64decode
from json import loads
from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissionFiltersBase
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


from capitolzen.organizations.models import Organization
from capitolzen.users.api.app.serializers import UserSerializer
from capitolzen.users.models import User
from capitolzen.users.api.app.serializers import AlertsSerializer
from capitolzen.users.models import Alert
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

    """

    """

    def get_queryset(self):
        org = Organization.objects.filter(users=self.request.user).last()
        users = org.users.all()
        return users
    """

    @list_route(methods=['GET'])
    def current(self, request):
        return Response(UserSerializer(request.user).data)

    permission_classes = (DRYPermissions, )
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_backends = (UserFilterBackend, DjangoFilterBackend)
    lookup_field = "id"


class AlertsFilterBackend(DRYPermissionFiltersBase):
    def filter_list_queryset(self, request, queryset, view):
        queryset = Alert.objects.filter(user=request.user)
        return queryset


class AlertsViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user
        return Alert.objects.filter(user=user)

    @list_route(methods=['GET'])
    def current(self, request):
        return Response(AlertsSerializer(request.user).data)

    @detail_route(methods=['POST'])
    def dismiss(self, request, id):
        alert = Alert.objects.get(id=id)
        alert.is_read = True
        alert.save()
        return Response(id, status=status.HTTP_200_OK)

    permission_classes = (DRYPermissions, )
    serializer_class = AlertsSerializer
    queryset = Alert.objects.get_queryset()
    filter_backends = (AlertsFilterBackend, DjangoFilterBackend)
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
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid request aaaa"},
                            status=status.HTTP_400_BAD_REQUEST)
