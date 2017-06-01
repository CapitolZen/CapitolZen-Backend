from rest_framework_json_api import serializers

from .models import Group, Comment


class GroupSerializer(serializers.ModelSerializer):
    organizations = ResourceRelatedField(
        many=False,
        read_only=True,
        source='organizations_organization'
    )
    class Meta:
        model = Group
        fields = ('id',)
        read_only_fields = ('id',)


class CommentSerializer(serializers.ModelSerializer):
    referenced_object = ResourceRelatedField(
        many=False,
        read_only=True,
    )
    class Meta:
        model = Comment
        fields = ('id',)
