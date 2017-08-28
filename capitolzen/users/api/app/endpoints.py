from django.core.mail import send_mail
from base64 import b64decode
from json import loads
from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissionFiltersBase
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import NotAuthenticated, NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from stream_django.feed_manager import feed_manager
from capitolzen.organizations.models import Organization
from capitolzen.users.api.app.serializers import UserSerializer
from capitolzen.organizations.api.app.serializers import OrganizationSerializer
from capitolzen.users.models import User, Notification
from rest_framework import status
from .serializers import ActivitySerializer
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from stream_django.client import stream_client
import random
from templated_email import send_templated_mail



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


class ActivityViewSet(viewsets.ViewSet):

    renderer_classes = (BrowsableAPIRenderer, JSONRenderer, )

    def _load_feed(self, request):
        """
        Format:
        user:current:notification

        <model>:<id>:<feed_name>
        :param request:
        :return:
        """
        raw_feed = request.query_params.get('feed', None)

        if raw_feed is None:
            return None

        elements = raw_feed.split(':')

        if len(elements) != 3:
            return None

        #
        # Real shoddy logic here.

        # Current user notification feed.
        if elements[0] == 'user' and elements[1] == 'current' and elements[2] == 'notification':
            return feed_manager.get_notification_feed(request.user.id)

        # Group feed
        if elements[0] == 'group' and elements[1] and elements[2] == 'timeline':
            return feed_manager.get_group_feed(elements[1])

        return None

    def list(self, request):
        verbs = [
            'join',
            'welcome',
            'provide',
            'like',
        ]
        actors = [
            1,
            2,
            3,
            4,
            5,
        ]
        limit = request.query_params.get('limit', None)

        feed = self._load_feed(request)

        if feed is None:
            raise NotFound(detail="Unable to load feed for: %s" % request.query_params.get('feed', None))

        activity_data = {
            'actor': random.choice(actors),
            'verb': random.choice(verbs),
            'object': request.user.id}

        feed.add_activity(activity_data)
        response = feed.get(limit=limit)

        send_templated_mail(
            template_name='welcome',
            from_email='from@example.com',
            recipient_list=['to@example.com'],
            context={
                "url": "https://www.google.com",
            },
        )

        return Response(response)
