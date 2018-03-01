from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api import serializers
from config.serializers import BaseInternalModelSerializer, RemoteFileField
from django.contrib.auth import get_user_model
from hashid_field.rest import HashidSerializerCharField

from capitolzen.organizations.models import Organization
from capitolzen.organizations.api.app.serializers import OrganizationSerializer
from capitolzen.users.models import User
from capitolzen.users.api.app.serializers import UserSerializer
from capitolzen.groups.models import Group, Report, Comment, File, ReportLink


class GroupSerializer(BaseInternalModelSerializer):
    included_serializers = {
        'organization': OrganizationSerializer,
    }

    organization = ResourceRelatedField(
        many=False,
        queryset=Organization.objects,
        required=False
    )
    avatar = RemoteFileField(required=False)

    assigned_to = ResourceRelatedField(
        queryset=get_user_model().objects,
        many=True,
        required=False,
    )

    class Meta:
        model = Group
        fields = (
            'id',
            'title',
            'organization',
            'active',
            'description',
            'created',
            'avatar',
            'assigned_to',
        )
        read_only_fields = ('id', 'created')

    class JSONAPIMeta:
       included_resources = ['organization']


class ReportSerializer(BaseInternalModelSerializer):
    included_serializers = {
        'user': UserSerializer,
        'organization': OrganizationSerializer,
        'group': GroupSerializer,
    }

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
            'user',
            'preferences',

        )

    class JSONAPIMeta:
       included_resources = ['user', 'organization', 'group']


class ReportLinkSerializer(BaseInternalModelSerializer):
    id = HashidSerializerCharField(source_field='groups.ReportLink.id')
    organization = ResourceRelatedField(
        many=False,
        queryset=Organization.objects
    )
    group = ResourceRelatedField(
        many=False,
        queryset=Group.objects
    )
    report = ResourceRelatedField(
        many=False,
        queryset=Report.objects
    )

    class Meta:
        model = ReportLink
        fields = (
            'id',
            'contact_list',
            'view_counter',
            'visibility',
            'report',
            'group',
            'organization'
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
