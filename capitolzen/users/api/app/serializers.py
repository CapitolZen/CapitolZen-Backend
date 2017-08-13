from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework.validators import UniqueValidator
from capitolzen.users.models import User, Alert


class UserSerializer(serializers.ModelSerializer):
    organizations = ResourceRelatedField(
        many=True,
        read_only=True,
        source='organizations_organization'
    )

    username = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ('id',
                  'created',
                  'modified',
                  'metadata',
                  'name',
                  'email',
                  'username',
                  'user_is_staff',
                  'user_is_admin',
                  'organizations',
                  'date_joined')
        read_only_fields = ('id',
                            'user_is_staff',
                            'user_is_admin',
                            'organizations',
                            'date_joined')
        lookup_field = 'id'

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class AlertsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alert
        fields = ('id', 'message', 'is_read', 'created', 'user', 'reference', 'bill_id')

    id = serializers.ReadOnlyField()
    message = serializers.ReadOnlyField(required=False)
