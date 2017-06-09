from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField

from .models import User


class UserSerializer(serializers.ModelSerializer):
    organizations = ResourceRelatedField(
        many=True,
        read_only=True,
        source='organizations_organization'
    )

    username = serializers.EmailField()

    class Meta:
        model = User
        fields = ('id', 'name', 'email',  'username', 'user_is_staff', 'user_is_admin', 'organizations')
        read_only_fields = ('username', 'id', 'user_is_staff', 'user_is_admin', 'organizations')
        lookup_field = 'username'

    def validate_username(self, attrs, source):
        """
        Customize the error message for a duplicate username.
        Use "email" instead of "username"
        """
        if self.object is None:
            username = attrs[source]
            if User._default_manager.filter(username=username).exists():
                raise serializers.ValidationError("That email is already being used.", code='duplicate_username')
        return attrs
