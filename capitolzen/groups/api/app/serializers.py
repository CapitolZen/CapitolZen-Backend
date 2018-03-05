from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api import serializers
from config.serializers import BaseInternalModelSerializer, RemoteFileField
from django.contrib.auth import get_user_model
from hashid_field.rest import HashidSerializerCharField

from capitolzen.organizations.models import Organization
from capitolzen.organizations.api.app.serializers import OrganizationSerializer

from capitolzen.proposals.models import Wrapper

from capitolzen.users.api.app.serializers import UserSerializer
from capitolzen.groups.models import Group, Report, File, Page, Link, Update


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
        queryset=get_user_model().objects
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
            'display_type',
        )

    class JSONAPIMeta:
       included_resources = ['user', 'organization', 'group']



class FileSerializer(BaseInternalModelSerializer):
    file = RemoteFileField()
    organization = ResourceRelatedField(
        many=False, queryset=Organization.objects
    )
    group = ResourceRelatedField(
        many=False,
        queryset=Group.objects
    )
    user = ResourceRelatedField(many=False, queryset=get_user_model().objects)
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
                  'description',
                  'group')
        read_only_fields = ('id',)


class PageSerializer(BaseInternalModelSerializer):
    id = HashidSerializerCharField()
    organization = ResourceRelatedField(
        many=False, queryset=Organization.objects
    )

    group = ResourceRelatedField(
        many=False,
        queryset=Group.objects
    )

    author = ResourceRelatedField(
        many=False, queryset=get_user_model().objects, required=False
    )

    included_serializers = {
        'author': UserSerializer,
        'organization': OrganizationSerializer,
        'group': GroupSerializer,
    }

    class Meta:
        model = Page
        fields = (
            'id',
            'metadata',
            'created',
            'modified',
            'visibility',
            'title',
            'description',
            'published',
            'organization',
            'group',
            'author'
        )

    class JSONAPIMeta:
       included_resources = ['author', 'organization', 'group']


class LinkSerializer(BaseInternalModelSerializer):
    url = serializers.URLField(),
    group = ResourceRelatedField(many=False, queryset=Group.objects)
    page = ResourceRelatedField(many=False, queryset=Page.objects)
    scraped_data = serializers.JSONField()

    included_serializers = {
        'organization': OrganizationSerializer,
        'group': GroupSerializer,
        'page': PageSerializer
    }

    class Meta:
        model = Link
        fields = ('id',
                  'metadata',
                  'created',
                  'modified',
                  'scraped_data')
        read_only_fields = ('id',)

        class JSONAPIMeta:
            included_resources = ['user', 'organization', 'group']



class UpdateSerializer(BaseInternalModelSerializer):
    user = ResourceRelatedField(
        many=False,
        queryset=get_user_model().objects
    )
    group = ResourceRelatedField(many=False, queryset=Group.objects)
    page = ResourceRelatedField(many=False, queryset=Page.objects)

    files = ResourceRelatedField(many=True, queryset=File.objects)
    links = ResourceRelatedField(many=True, queryset=Link.objects)
    wrappers = ResourceRelatedField(many=True, queryset=Wrapper.objects)
    reports = ResourceRelatedField(many=True, queryset=Report.objects)

    document = serializers.JSONField()

    class Meta:
        model = Update
        fields = (
            'id',
            'user',
            'group',
            'page',
            'document',
            'title',

        )
