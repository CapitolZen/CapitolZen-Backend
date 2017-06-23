from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from capitolzen.organizations.models import Organization
from capitolzen.users.models import User
from .models import Group, Report, Comment


class GroupSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Organization.objects
    )

    class Meta:
        model = Group
        fields = ('id', 'title', 'organization', 'attachments',
                  'contacts', 'description', 'logo', 'created')
        read_only_fields = ('id',)


class ReportSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=User.objects
    )
    organization = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Organization.objects
    )
    group = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Group.objects
    )

    class Meta:
        model = Report
        fields = ('id', 'created', 'organization', 'group', 'bills',
                  'attachments', 'status', 'scheduled', 'publish_date', 'author')


class CommentSerializer(serializers.ModelSerializer):
    referenced_object = ResourceRelatedField(
        many=False,
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id',)
