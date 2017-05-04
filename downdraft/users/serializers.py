from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField

from .models import User


class UserSerializer(serializers.ModelSerializer):
    organizations = ResourceRelatedField(
        many=True,
        read_only=True,
        source='organizations_organization'
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'provider_info', 'user_is_staff',
                  'user_is_admin', 'organizations')
        read_only_fields = ('username', )
        lookup_field = 'username'
