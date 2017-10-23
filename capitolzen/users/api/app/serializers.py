from django.contrib.auth import get_user_model

from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework.validators import UniqueValidator

from config.serializers import BaseInternalModelSerializer, RemoteFileField

from capitolzen.organizations.api.app.serializers import OrganizationSerializer
from capitolzen.organizations.notifications import email_owner_welcome
from capitolzen.users.utils import token_decode, token_encode
from capitolzen.users.notifications import email_user_password_reset_request


User = get_user_model()


class UserSerializer(BaseInternalModelSerializer):
    """
    Model: User

    """
    organizations = ResourceRelatedField(
        many=True,
        read_only=True,
        source='organizations_organization'
    )

    username = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Email address is already in use",
            )]
    )
    avatar = RemoteFileField(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'created',
            'modified',
            'name',
            'username',
            'is_staff',
            'is_superuser',
            'organizations',
            'date_joined',
            'avatar',
        )
        read_only_fields = (
            'id',
            'is_staff',
            'is_superuser',
            'organizations',
            'date_joined',
        )
        lookup_field = 'id'


class RegistrationSerializer(serializers.Serializer):
    """
    User registration serializer. Creates a user and an org.
    """

    # User Fields
    name = serializers.CharField()
    username = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Email address is already in use",
            )]
    )
    confirm_password = serializers.CharField()
    password = serializers.CharField()

    # Organization Fields
    organization_name = serializers.CharField()

    def validate(self, data):
        """
        TODO: We're currently passing org data into the user serializer model.
        This might cause conflicts. Consider doing something smarter.
        :param data:
        :return:
        """
        #
        # User Validation

        # Perform server side validation
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                'Password and Confirm Password should be the same'
            )

        user_serializer = UserSerializer(data=data)
        user_serializer.is_valid(raise_exception=True)

        organization_data = {
            'name': data['organization_name']
        }

        organization_serializer = OrganizationSerializer(data=organization_data)
        organization_serializer.is_valid(raise_exception=True)

        data['user_serializer'] = user_serializer
        data['organization_serializer'] = organization_serializer

        return data

    def save(self, **kwargs):
        user_serializer = self.validated_data['user_serializer']
        organization_serializer = self.validated_data['organization_serializer']

        #
        # Make the user first
        user_serializer.save()
        user = user_serializer.instance
        user.set_password(self.validated_data['password'])
        user.save()

        #
        # Do organization things
        organization_serializer.save()
        organization = organization_serializer.instance
        organization.add_user(user)

        email_owner_welcome(user.username, name=user.name)

        return True

    class Meta:
        model = User


class ResetPasswordRequestSerializer(serializers.Serializer):
    """
    Request a new password. Sends an email.
    """
    email = serializers.EmailField()

    def save(self, **kwargs):
        # We don't want to expose that a user may or may not exist
        # Using the password reset form. So we load the user during save
        # and fail silently if we can't find it.
        try:
            user = User.objects.get(username=self.validated_data['email'])
        except User.DoesNotExist:
            return True

        #
        # Again, don't tell the requestor anything about the
        # permissions of the user.
        if user.is_staff or user.is_superuser:
            return True

        token = token_encode(user, action='reset_password')
        email_user_password_reset_request(user.username, token=token)
        return True

    class Meta:
        model = User


class ResetPasswordSerializer(serializers.Serializer):
    """
    Updates password based on token and new password.
    """
    token = serializers.CharField()
    confirm_password = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        # Perform server side validation
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                'Password and Confirm Password should be the same'
            )

        payload = token_decode(data['token'])
        if not payload:
            raise serializers.ValidationError("Unable to decode token")

        if payload.get('action') != 'reset_password':
            raise serializers.ValidationError("Invalid Token")

        data['token_payload'] = payload

        try:
            user = User.objects.get(username=payload['username'])
            data['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError("Unable to load user")

        return data

    def save(self, **kwargs):
        user = self.validated_data['user']
        user.set_password(self.validated_data['password'])
        user.save()

        return {
            'email': user.username
        }

    class Meta:
        model = User


class ChangePasswordSerializer(serializers.Serializer):
    """
    When a user is logged in, allow them to change their own password
    """
    current_password = serializers.CharField()
    confirm_password = serializers.CharField()
    password = serializers.CharField()
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.get_queryset()
    )

    def validate(self, data):
        # Check current password
        if not data['user'].check_password(data['current_password']):
            raise serializers.ValidationError(
                'Current password is not correct'
            )

        # Perform server side validation
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                'Password and Confirm Password should be the same'
            )

        return data

    def save(self, **kwargs):
        user = self.validated_data['user']
        user.set_password(self.validated_data['password'])
        user.save()
        return True

    class Meta:
        model = User
