from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from capitolzen.organizations.models import Organization
from capitolzen.groups.models import Group
from capitolzen.proposals.models import Bill, Wrapper


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = ('id', 'state', 'title', 'sponsor', 'summary', 'last_action_date', 'remote_url',
                  'status', 'state_id', 'state', 'current_committee', 'affected_section')


class WrapperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wrapper
        fields = ('id', 'bill', 'group', 'organization', 'notes', 'position')

    bill = ResourceRelatedField(many=False, queryset=Bill.objects)
    organization = ResourceRelatedField(many=False, queryset=Organization.objects)
    group = ResourceRelatedField(many=False, queryset=Group.objects)
    id = serializers.ReadOnlyField()

