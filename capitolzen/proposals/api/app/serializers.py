from django.db import transaction

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
            'remote_status',
            'history',
            'current_committee',
            'sponsor',
            'sponsors',
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

    def create(self, validated_data):
        from capitolzen.proposals.tasks import ingest_attachment
        remote_id = validated_data.pop('remote_id')
        if validated_data.get('state'):
            validated_data['state'] = validated_data.get('state').upper()
        instance, _ = Bill.objects.get_or_create(
            remote_id=remote_id,
            defaults={
                **validated_data
            }
        )
        instance = instance.update(validated_data)
        transaction.on_commit(
            lambda: ingest_attachment.apply_async(kwargs={
                "identifier": str(instance.pk)
            }))
        return instance

    def update(self, instance, validated_data):
        from capitolzen.proposals.tasks import ingest_attachment
        instance = instance.update(validated_data)
        transaction.on_commit(
            lambda: ingest_attachment.apply_async(kwargs={
                "identifier": str(instance.pk)
            }))
        return instance


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
            'full_name',
            'created_at',
            'updated_at'
        )

    def create(self, validated_data):
        remote_id = validated_data.pop('remote_id')
        instance, _ = Legislator.objects.get_or_create(
            remote_id=remote_id,
            defaults={
                **validated_data
            }
        )

        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CommitteeSerializer(BaseModelSerializer):
    class Meta:
        model = Committee
        fields = (
            'name',
            'state',
            'chamber',
            'remote_id',
            'parent_id',
            'subcommittee',
            'created_at',
            'updated_at'
        )

    def create(self, validated_data):
        remote_id = validated_data.pop('remote_id')
        instance, _ = Committee.objects.get_or_create(
            remote_id=remote_id,
            defaults={
                **validated_data
            }
        )

        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


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
            'position_detail',
            'files',
        )

    def create(self, validated_data):
        bill = validated_data.get('bill')
        group = validated_data.get('group')
        queryset = Wrapper.objects.filter(bill_id=bill.id, group_id=group.id)
        if queryset.exists():
            raise ValidationError('Wrapper already exists for this data')
        return Wrapper.objects.create(**validated_data)
