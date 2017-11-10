import base64
import requests

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

    current_committee = ResourceRelatedField(
        many=False,
        queryset=Legislator.objects
    )

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
        instance, created = Bill.objects.get_or_create(
            remote_id=remote_id,
            defaults={
                **validated_data
            }
        )
        if instance.modified < validated_data.get('updated_at') or created:
            instance.update_from_source(validated_data)
            if instance.bill_versions:
                instance.current_version = instance.bill_versions[-1].get('url')
            if instance.current_version:
                response = requests.get(instance.current_version)
                if 200 >= response.status_code < 300:
                    instance.bill_raw_text = base64.b64encode(
                        response.content).decode('ascii')

            committee = self.get_current_committee(instance)
            if committee:
                instance.current_committee = committee
            instance.save()
        transaction.on_commit(
            lambda: ingest_attachment.apply_async(kwargs={
                "identifier": str(instance.pk)
            }))
        return instance

    @staticmethod
    def get_current_committee(instance):
        committee = None
        chamber = None
        for action in instance.history:
            if action.type == 'committee:referred':
                action_parts = action.action.lower().split('referred to committee ')
                committee = action_parts[0]
                chamber = action.actor
            if action.type == 'committee:passed':
                committee = None
                chamber = None

        if committee and chamber:
            return Committee.objects.filter(name__icontains=committee, chamber=chamber).first()
        else:
            return None


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
        instance, created = Legislator.objects.get_or_create(
            remote_id=remote_id,
            defaults={
                **validated_data
            }
        )
        if instance.modified < validated_data.get('updated_at') or not created:
            for attr, value in validated_data.iteritems():
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
        instance, created = Committee.objects.get_or_create(
            remote_id=remote_id,
            defaults={
                **validated_data
            }
        )
        if instance.modified < validated_data.get('updated_at') and not created:
            for attr, value in validated_data.iteritems():
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
