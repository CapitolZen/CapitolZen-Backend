from rest_framework_json_api.relations import ResourceRelatedField

from config.serializers import BaseInternalModelSerializer

from capitolzen.organizations.models import Organization
from capitolzen.users.models import User
from capitolzen.groups.models import Group, Report, Comment


class GroupSerializer(BaseInternalModelSerializer):
    organization = ResourceRelatedField(
        many=False,
        queryset=Organization.objects
    )

    class Meta:
        model = Group
        fields = (
            'title',
            'organization',
            'attachments',
            'active',
            'contacts',
            'description',
            'logo',
            'starred',
        )
        read_only_fields = ('id',)


class ReportSerializer(BaseInternalModelSerializer):
    user = ResourceRelatedField(
        many=False,
        queryset=User.objects
    )
    organization = ResourceRelatedField(
        many=False,
        queryset=Organization.objects
    )
    group = ResourceRelatedField(
        many=False,
        queryset=Group.objects
    )

    class Meta:
        model = Report
        fields = (
            'organization',
            'group',
            'filter',
            'title',
            'description',
            'attachments',
            'status',
            'scheduled',
            'publish_date',
            'user',
            'preferences'
        )


class CommentSerializer(BaseInternalModelSerializer):
    referenced_object = ResourceRelatedField(
        many=False,
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id',)
