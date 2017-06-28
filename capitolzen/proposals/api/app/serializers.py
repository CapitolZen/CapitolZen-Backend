from rest_framework_json_api import serializers
from capitolzen.organizations.models import Organization
from capitolzen.proposals.models import Bill, Wrapper


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = ('id', 'state', 'title', 'sponsor', 'summary', 'status', 'state_id', 'state')


class WrapperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wrapper
        fields = ('id', 'bill', 'groups', 'organization', 'notes')

    bill = serializers.PrimaryKeyRelatedField(many=False, queryset=Bill.objects)
    organization = serializers.PrimaryKeyRelatedField(many=False, queryset=Organization.objects)
    id = serializers.ReadOnlyField()

