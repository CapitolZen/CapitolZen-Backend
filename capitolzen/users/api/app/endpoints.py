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
from stream_django.feed_manager import feed_manager
from capitolzen.organizations.models import Organization
from capitolzen.users.api.app.serializers import UserSerializer
from capitolzen.organizations.api.app.serializers import OrganizationSerializer
from capitolzen.users.models import User, Notification
from rest_framework import status
from rest_framework.exceptions import NotFound
from .serializers import ActivitySerializer
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer


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

    @list_route(methods=['GET'])
    def current(self, request):
        return Response(UserSerializer(request.user).data)

    @list_route(methods=['post'])
    def register(self, request):

        #
        # We prepare both the organization and user models
        # before saving either so that errors are raised prior
        # to anything being created

        userSerializer = UserSerializer(data=request.data)
        userSerializer.is_valid(raise_exception=True)

        orgData = {
            'name': request.data['organizationName']
        }

        organizationSerializer = OrganizationSerializer(data=orgData)
        organizationSerializer.is_valid(raise_exception=True)

        #
        # Make the user first
        userSerializer.save()
        user = userSerializer.instance
        user.set_password(request.data['password'])
        user.save()

        #
        # Do organization things
        organizationSerializer.save()
        organization = organizationSerializer.instance
        organization.add_user(user)
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
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid request aaaa"},
                            status=status.HTTP_400_BAD_REQUEST)


class ActivityViewSet(viewsets.ViewSet):

    renderer_classes = (BrowsableAPIRenderer, JSONRenderer, )

    def list(self, request):
        notification_feed = feed_manager.get_notification_feed(request.user.id)
        activity_data = {'actor': request.user.id, 'verb': 'joined', 'object': request.user.id}
        notification_feed.add_activity(activity_data)
        response = notification_feed.get(mark_seen=False, mark_read=False)
        return Response(response)
        """

        pprint(response)

        results = response.get('results', None)

        if not results:
            raise NotFound()

        results = results[0]

        activities = results.get('activities', None)

        if not activities or not len(activities):
            raise NotFound()

        return Response(ActivitySerializer(activities, many=True).data)
        """
