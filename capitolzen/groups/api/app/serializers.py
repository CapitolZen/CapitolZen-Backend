from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api import serializers
from config.serializers import BaseInternalModelSerializer, RemoteFileField
from capitolzen.organizations.models import Organization
from capitolzen.users.models import User
from django.contrib.auth import get_user_model
from capitolzen.groups.models import Group, Report, Comment, File


class GroupSerializer(BaseInternalModelSerializer):
    organization = ResourceRelatedField(
        many=False,
        queryset=Organization.objects,
        required=False
    )
    avatar = RemoteFileField(required=False)

    assigned_to = ResourceRelatedField(
        queryset=get_user_model().objects,
        many=True
    )

    class Meta:
        model = Group
        fields = (
            'id',
            'title',
            'organization',
            'attachments',
            'active',
            'contacts',
            'description',
            'user_list',
            'created',
            'avatar',
            'assigned_to',
        )
        read_only_fields = ('id', 'created')


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
            'id',
            'created',
            'modified',
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


class FileSerializer(BaseInternalModelSerializer):
    file = RemoteFileField()
    organization = ResourceRelatedField(
        many=False, queryset=Organization.objects
    )
    user = ResourceRelatedField(many=False, queryset=User.objects)
    user_path = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    description = serializers.CharField(allow_blank=True, required=False, allow_null=True)

    class Meta:
        model = File
        fields = ('id',
                  'metadata',
                  'created',
                  'modified',
                  'visibility',
                  'user_path',
                  'organization',
                  'user',
                  'name',
                  'file',
                  'description')
        read_only_fields = ('id',)
