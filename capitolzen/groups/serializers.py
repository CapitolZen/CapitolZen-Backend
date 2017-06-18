from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField

from .models import Group, Comment


class GroupSerializer(serializers.ModelSerializer):
    organization = ResourceRelatedField(
        many=False,
        read_only=True
    )

    class Meta:
        model = Group
        fields = ('id', 'title', 'organization', 'attachments', 'contacts', 'description')
        read_only_fields = ('id', 'organization')


class CommentSerializer(serializers.ModelSerializer):
    referenced_object = ResourceRelatedField(
        many=False,
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id',)
