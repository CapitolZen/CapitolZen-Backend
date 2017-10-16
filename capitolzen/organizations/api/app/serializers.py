from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from capitolzen.organizations.models import (Organization, OrganizationInvite, File)
from capitolzen.users.models import User
from config.serializers import RemoteFileField


class OrganizationSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    avatar = RemoteFileField(required=False)

    class Meta:
        model = Organization
        fields = (
            'id',
            'name',
            'is_active',
            'billing_email',
            'billing_phone',
            'billing_address_one',
            'billing_name',
            'billing_address_two',
            'billing_city',
            'billing_state',
            'billing_zip_code',
            'stripe_payment_tokens',
            'plan_name',
            'avatar',
        )

    def create(self, validated_data):
        org = Organization.objects.create(**validated_data)
        org.is_active = True
        org.save()
        return org


class OrganizationInviteSerializer(serializers.ModelSerializer):

    def validate_username(self, value):
        """
        Check if email is currently in use
        :return:
        """
        try:
            user = User.objects.get(username=value)
            raise serializers.ValidationError("Email Already In Use")

        except User.DoesNotExist:
            pass

        return value

    class Meta:
        model = OrganizationInvite
        fields = ('id',
                  'metadata',
                  'created',
                  'modified',
                  'organization',
                  'organization_name',
                  'email',
                  'status')


class FileSerializer(serializers.ModelSerializer):
    file = RemoteFileField()
    organization = ResourceRelatedField(many=False, queryset=Organization.objects)
    user = ResourceRelatedField(many=False, queryset=User.objects)

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
                  'name')
        read_only_fields = ('id',)
