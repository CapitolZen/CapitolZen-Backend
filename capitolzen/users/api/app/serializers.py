from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField

from rest_framework.validators import UniqueValidator

from config.serializers import BaseInternalModelSerializer
from capitolzen.users.models import User


class UserSerializer(BaseInternalModelSerializer):
    """
    Generic user serializer
    """
    organizations = ResourceRelatedField(
        many=True,
        read_only=True,
        source='organizations_organization'
    )

    username = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'name',
            'username',
            'is_staff',
            'is_superuser',
            'organizations',
            'date_joined'
        )
        read_only_fields = (
            'id',
            'is_staff',
            'is_superuser',
            'organizations',
            'date_joined'
        )
        lookup_field = 'id'


class ActivitySerializer(serializers.Serializer):
    """

    """
    actor = serializers.IntegerField()
    verb = serializers.CharField()
    id = serializers.CharField()
    origin = serializers.CharField()
    object = serializers.CharField()
    target = serializers.CharField()
    to = serializers.ListField()
    time = serializers.DateTimeField()


