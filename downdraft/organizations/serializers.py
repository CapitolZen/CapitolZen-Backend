from rest_framework_json_api import serializers
from dry_rest_permissions.generics import DRYPermissionsField

from .models import (Organization, OrganizationInvite)


class OrganizationSerializer(serializers.ModelSerializer):
    permissions = DRYPermissionsField()
    user_is_member = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()

    class Meta:
        model = Organization
        fields = (
            'id', 'name', 'is_active', 'user_is_owner', 'billing_email', 'billing_phone',
            'user_is_admin', 'user_is_member', 'demographic_org_type', 'billing_address_one',
            'billing_address_two', 'billing_city', 'billing_state', 'billing_zip_code', 'plan_type',
            'stripe_payment_methods', 'permissions'
        )


class OrganizationInviteSerializer(serializers.ModelSerializer):
    permissions = DRYPermissionsField()

    class Meta:
        model = OrganizationInvite
        fields = ('id', 'organization', 'organization_name',
                  'created', 'modified', 'email', 'status',
                  'permissions')
