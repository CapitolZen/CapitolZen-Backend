from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api import serializers
from config.serializers import BaseInternalModelSerializer, RemoteFileField
from django.contrib.auth import get_user_model
from hashid_field.rest import HashidSerializerCharField

from capitolzen.organizations.models import Organization
from capitolzen.organizations.api.app.serializers import OrganizationSerializer, AnonOrganizationSerializer

from capitolzen.proposals.models import Wrapper

from capitolzen.groups.models import Group, Report, File, Page, Link, Update


class GroupSerializer(BaseInternalModelSerializer):
    included_serializers = {
        'organization': OrganizationSerializer,
        'assigned_to': 'users.api.app.serializers.UserSerializer',
        'guest_users': 'users.api.app.serializers.UserSerializer'
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

    guest_users = ResourceRelatedField(
        queryset=get_user_model().objects,
        many=True,
        required=False
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
            'guest_users'
        )
        read_only_fields = ('id', 'created')

    class JSONAPIMeta:
       included_resources = ['organization', 'assigned_to', 'guest_users']


class AnonGroupSerializer(BaseInternalModelSerializer):
    included_serializers = {
        'organization': OrganizationSerializer,
        'assigned_to': 'users.api.app.serializers.UserSerializer',
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
            'avatar',
            'assigned_to',
        )
        read_only_fields = ('id', 'created')

    class JSONAPIMeta:
       included_resources = ['organization', 'assigned_to']


class ReportSerializer(BaseInternalModelSerializer):
    included_serializers = {
        'user': 'users.api.app.serializers.UserSerializer',
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
       included_resources = ['user', 'group']



class FileSerializer(BaseInternalModelSerializer):
    file = RemoteFileField()
    organization = ResourceRelatedField(
        many=False, queryset=Organization.objects
    )
    group = ResourceRelatedField(
        many=False,
        queryset=Group.objects,
        required=False
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
    id = HashidSerializerCharField(source_field='groups.Page.id', required=False)
    organization = ResourceRelatedField(
        many=False, queryset=Organization.objects
    )

    group = ResourceRelatedField(
        many=False,
        queryset=Group.objects
    )

    author = ResourceRelatedField(
        many=False, queryset=get_user_model().objects
    )

    bill_layout = serializers.ChoiceField(
        choices=['table', 'slides', 'list'],
        required=False
    )

    visibility = serializers.ChoiceField(
        choices=['anyone', 'organization']
    )

    viewers = ResourceRelatedField(
        queryset=get_user_model().objects,
        many=True,
        required=False
    )

    included_serializers = {
        'author': 'users.api.app.serializers.UserSerializer',
        'organization': AnonOrganizationSerializer,
        'group': AnonGroupSerializer,
        'viewers': 'users.api.app.serializers.UserSerializer'
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
            'author',
            'bill_layout',
            'avatar',
            'viewers',
            'structured_page_info'
        )
        read_only_fields = ('id',)

    class JSONAPIMeta:
       included_resources = ['author', 'organization', 'group', 'viewers']


class LinkSerializer(BaseInternalModelSerializer):
    url = serializers.URLField(),
    group = ResourceRelatedField(many=False, queryset=Group.objects)
    page = ResourceRelatedField(many=False, queryset=Page.objects)
    scraped_data = serializers.JSONField()

    included_serializers = {
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
        included_resources = ['page', 'group']



class UpdateSerializer(BaseInternalModelSerializer):
    user = ResourceRelatedField(
        many=False,
        queryset=get_user_model().objects
    )

    included_serializers = {
        'group': AnonGroupSerializer,
        'page': PageSerializer,
        'user': 'users.api.app.serializers.UserSerializer',
        'files': FileSerializer,
        'wrappers': 'proposals.api.app.serializers.WrapperSerializer'
    }

    group = ResourceRelatedField(many=False, queryset=Group.objects)
    page = ResourceRelatedField(pk_field=HashidSerializerCharField(source_field='groups.Page.id'), queryset=Page.objects.all(), many=False)
    organization = ResourceRelatedField(many=False, queryset=Organization.objects)
    files = ResourceRelatedField(many=True, queryset=File.objects, required=False)
    links = ResourceRelatedField(many=True, queryset=Link.objects, required=False)
    wrappers = ResourceRelatedField(many=True, queryset=Wrapper.objects, required=False)
    reports = ResourceRelatedField(many=True, queryset=Report.objects, required=False)

    document = serializers.JSONField(required=False)

    class Meta:
        model = Update
        fields = (
            'id',
            'user',
            'group',
            'organization',
            'page',
            'document',
            'title',
            'published',
            'reports',
            'wrappers',
            'files',
            'links',
            'created',
            'modified'
        )

    class JSONAPIMeta:
        included_resources = ['user', 'page', 'page.organization', 'group', 'files', 'wrappers', 'wrappers.bill',
                              'wrappers.bill.sponsor']


class UpdateSerializerPageable(UpdateSerializer):
    next = serializers.SerializerMethodField()
    prev = serializers.SerializerMethodField()

    # Note: these are backwards because there's not a way to apply the correct descending sorting here
    def get_next(self, obj):
        try:
            return obj.get_previous_by_created(page=obj.page).id
        except:
            return None

    def get_prev(self, obj):
        try:
            return str(obj.get_next_by_created(page=obj.page).id)
        except:
            return None

    class Meta(UpdateSerializer):
        model = Update
        fields = (
            'prev',
            'next',
        ) + UpdateSerializer.Meta.fields


