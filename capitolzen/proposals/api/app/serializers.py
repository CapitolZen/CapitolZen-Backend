from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from capitolzen.organizations.models import Organization
from capitolzen.groups.models import Group
from capitolzen.proposals.models import Bill, Wrapper, Legislator, Committee


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = '__all__'


class LegilsatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Legislator
        fields = '__all__'


class CommitteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Committee
        fields = '__all__'


class WrapperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wrapper
        fields = ('id', 'bill', 'group', 'organization', 'notes', 'position', 'summary', 'position_detail')

    bill = ResourceRelatedField(many=False, queryset=Bill.objects)
    organization = ResourceRelatedField(many=False, queryset=Organization.objects)
    group = ResourceRelatedField(many=False, queryset=Group.objects)
    id = serializers.ReadOnlyField()

