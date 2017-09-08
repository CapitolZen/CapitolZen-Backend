from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from capitolzen.organizations.models import Organization
from capitolzen.groups.models import Group
from capitolzen.proposals.models import Bill, Wrapper, Legislator, Committee


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = (
            'state',
            'state_id',
            'id', 'type',
            'session',
            'chamber',
            'remote_id',
            'status',
            'history',
            'current_committee',
            'sponsor',
            'title',
            'categories',
            'remote_url',
            'affected_section',
            'sources',
            'action_dates',
            'documents',
            'cosponsors',
            'votes',
            'last_action_date',
            'companions',
            'bill_versions',
            'introduced_date'
        )


class LegislatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Legislator
        fields = (
            'remote_id',
            'state',
            'active',
            'chamber',
            'party',
            'district',
            'email',
            'url',
            'photo_url',
            'first_name',
            'middle_name',
            'last_name',
            'suffixes',
            'full_name'
        )


class CommitteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Committee
        fields = (
            'name',
            'state',
            'chamber',
            'remote_id',
            'parent_id',
            'subcommittee'
        )


class WrapperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wrapper
        fields = (
            'id',
            'bill',
            'group',
            'organization',
            'notes',
            'position',
            'summary',
            'position_detail'
        )

    bill = ResourceRelatedField(many=False, queryset=Bill.objects)
    organization = ResourceRelatedField(
        many=False, queryset=Organization.objects
    )
    group = ResourceRelatedField(many=False, queryset=Group.objects)
    id = serializers.ReadOnlyField()

