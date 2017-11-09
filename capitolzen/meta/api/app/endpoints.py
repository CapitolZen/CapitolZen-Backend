"""
TODO: Move this around to a better location in the codebase.
"""
import random
from mimetypes import guess_extension
from uuid import uuid4

from django.conf import settings
from rest_framework import viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from stream_django.feed_manager import feed_manager

from capitolzen.utils.s3 import get_s3_client


class FileManagerView(APIView):

    def get(self, request, format=None):
        file_type = request.query_params.get('type')

        if not file_type:
            raise ValidationError(detail="Must provide file type")

        file_extension = guess_extension(file_type)
        if not file_extension:
            raise ValidationError(
                detail="Cannot determine file extension for type provided"
            )

        s3 = get_s3_client()

        # Make sure everything posted is publicly readable
        fields = {
            "acl": "public-read",
            "Content-Type": file_type,
        }

        # Ensure that the ACL isn't changed
        conditions = [
            {
                "acl": "public-read",
            },
            {
                "Content-Type": file_type,
            },
        ]

        file_name = "%s%s" % (uuid4(), file_extension)

        # Generate the POST attributes
        post = s3.generate_presigned_post(
            Bucket=settings.AWS_TEMP_BUCKET_NAME,
            Key=file_name,
            Fields=fields,
            Conditions=conditions
        )

        return Response(post)


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
        if elements[0] == 'user' and elements[1] == 'current' and \
                elements[2] == 'notification':
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
            raise NotFound(
                detail="Unable to load feed for: %s" % request.query_params.get(
                    'feed', None
                ))

        activity_data = {
            'actor': random.choice(actors),
            'verb': random.choice(verbs),
            'object': request.user.id}

        feed.add_activity(activity_data)
        response = feed.get(limit=limit)

        return Response(response)
