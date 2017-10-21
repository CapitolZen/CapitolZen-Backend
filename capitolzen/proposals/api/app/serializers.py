from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework.serializers import ValidationError

from config.serializers import (
    BaseModelSerializer,
    BaseInternalModelSerializer
)

from capitolzen.organizations.models import Organization
from capitolzen.groups.models import Group
from capitolzen.proposals.models import Bill, Wrapper, Legislator, Committee


class BillSerializer(BaseModelSerializer):
    class Meta:
        model = Bill
        fields = (
            'state',
            'state_id',
            'type',
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
            'introduced_date',
            'created_at',
            'updated_at'
        )

    def validate_type(self, data):
        if isinstance(list, data):
            return ",".join(data)
        return data

    def create(self, validated_data):
        remote_id = validated_data.pop('remote_id')
        bill, created = Bill.objects.get_or_create(
            remote_id=remote_id,
            defaults={
                **validated_data
            }
        )
        if bill.modified < validated_data.get('updated_at') or created:
            bill.update_from_source(validated_data)
            if bill.bill_versions:
                bill.current_version = bill.bill_versions[-1].get('url')
            bill.save()
        return bill


class LegislatorSerializer(BaseModelSerializer):
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


class CommitteeSerializer(BaseModelSerializer):
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


class WrapperSerializer(BaseInternalModelSerializer):
    bill = ResourceRelatedField(many=False, queryset=Bill.objects)
    organization = ResourceRelatedField(
        many=False, queryset=Organization.objects
    )
    group = ResourceRelatedField(many=False, queryset=Group.objects)

    class Meta:
        model = Wrapper
        fields = (
            'bill',
            'group',
            'organization',
            'notes',
            'position',
            'summary',
            'position_detail'
        )

    def create(self, validated_data):
        print(validated_data)
        bill = validated_data.get('bill')
        group = validated_data.get('group')
        print(bill.id)
        print(group.id)
        queryset = Wrapper.objects.filter(bill_id=bill.id, group_id=group.id)
        print(queryset)
        if queryset.exists():
            raise ValidationError('Wrapper already exists for this data')
        return Wrapper.objects.create(**validated_data)
