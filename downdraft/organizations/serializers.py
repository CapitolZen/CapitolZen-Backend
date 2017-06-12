from rest_framework_json_api import serializers
from crum import get_current_user
from dry_rest_permissions.generics import DRYPermissionsField
from pprint import pprint
from .models import (Organization, OrganizationInvite)


class OrganizationSerializer(serializers.ModelSerializer):
    permissions = DRYPermissionsField()
    user_is_member = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()
    demographic_org_type = serializers.ChoiceField(
        choices=Organization.ORG_DEMO,
        default='individual'
    )

    plan_type = serializers.ChoiceField(
         choices=Organization.PLAN_CHOICES,
         default=Organization.PLAN_DEFAULT
    )

    class Meta:
        model = Organization
        fields = (
            'id', 'name', 'is_active', 'user_is_owner', 'billing_email', 'billing_phone',
            'user_is_admin', 'user_is_member', 'demographic_org_type', 'billing_address_one',
            'billing_address_two', 'billing_city', 'billing_state', 'billing_zip_code', 'plan_type',
            'stripe_payment_methods', 'permissions'
        )

    def create(self, validated_data):
        org = Organization.objects.create(**validated_data)
        org.save()
        return org


class OrganizationInviteSerializer(serializers.ModelSerializer):
    permissions = DRYPermissionsField()

    class Meta:
        model = OrganizationInvite
        fields = ('id', 'organization', 'organization_name',
                  'created', 'modified', 'email', 'status',
                  'permissions')
