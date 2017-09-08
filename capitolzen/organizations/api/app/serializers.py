from rest_framework_json_api import serializers

from config.serializers import BaseInternalModelSerializer

from capitolzen.organizations.models import (Organization, OrganizationInvite)
from capitolzen.users.models import User


class OrganizationSerializer(BaseInternalModelSerializer):
    user_is_member = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = Organization
        fields = (
            'name',
            'is_active',
            'user_is_owner',
            'billing_email',
            'billing_phone',
            'user_is_admin',
            'user_is_member',
            'billing_address_one',
            'billing_name',
            'billing_address_two',
            'billing_city',
            'billing_state',
            'billing_zip_code',
            'stripe_payment_tokens',
            'plan_name',
            'logo'
        )

    def create(self, validated_data):
        org = Organization.objects.create(**validated_data)
        org.is_active = True
        org.save()
        return org


class OrganizationInviteSerializer(BaseInternalModelSerializer):

    def validate_username(self, value):
        """
        Check if email is currently in use
        :return:
        """
        try:
            User.objects.get(username=value)
            raise serializers.ValidationError("Email Already In Use")
        except User.DoesNotExist:
            pass

        return value

    class Meta:
        model = OrganizationInvite
        fields = (
            'organization',
            'organization_name',
            'email',
            'status'
        )

