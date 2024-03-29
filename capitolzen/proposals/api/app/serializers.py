from django.db import transaction
from django.conf import settings

from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework.serializers import ValidationError

from config.serializers import (
    BaseModelSerializer,
    BaseInternalModelSerializer
)

from capitolzen.groups.models import Group
from capitolzen.groups.api.app.serializers import GroupSerializer
from capitolzen.proposals.models import Bill, Wrapper, Legislator, Committee, Event

from rest_framework import serializers


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


class BillSerializer(BaseModelSerializer):
    included_serializers = {
        'sponsor': LegislatorSerializer,
        'current_committee': CommitteeSerializer
    }

    current_committee = ResourceRelatedField(
        many=False,
        queryset=Committee.objects,
        required=False
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
            'updated_at',
            'bill_text_analysis',
            'related_bill_ids'
        )

    class JSONAPIMeta:
        included_resources = ['sponsor', 'current_committee']

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


class EventSerializer(BaseInternalModelSerializer):
    committee = ResourceRelatedField(many=False, queryset=Committee.objects, required=False, allow_null=True)
    legislator = ResourceRelatedField(many=False, queryset=Legislator.objects, required=False, allow_null=True)
    created = serializers.DateTimeField(
        format=settings.API_DATETIME_FORMAT,
        read_only=True,
        help_text="ISO 8601 formatted timestamp identifying when the object "
                  "was created in the database."
    )
    class Meta:
        model = Event
        fields = (
            'committee',
            'legislator',
            'event_type',
            'chamber',
            'state',
            'created',
            'modified',
            'attachments',
            'location_text',
            'time',
            'url',
            'description'
        )


class WrapperSerializer(BaseInternalModelSerializer):
    included_serializers = {
        'bill': BillSerializer,
        'bill.sponsor': LegislatorSerializer,
        'group': GroupSerializer,
        'bill.current_committee': CommitteeSerializer
    }

    bill = ResourceRelatedField(
        many=False, queryset=Bill.objects,
        required=False,
        allow_null=True)

    organization = ResourceRelatedField(
        many=False,
        read_only=True,
    )

    group = ResourceRelatedField(
        many=False,
        queryset=Group.objects
    )

    def validate(self, attrs):
        """
        We don't allow the frontend to dictate the organization.
        :param attrs:
        :return:
        """
        if not self.context.get('request').organization:
            raise serializers.ValidationError(detail="Cannot create without an organization")

        attrs['organization'] = self.context.get('request').organization
        return attrs

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
            'metadata'
        )

    class JSONAPIMeta:
        included_resources = ['bill', 'bill.sponsor', 'group', 'bill.current_committee']

    def create(self, validated_data):
        """
        This is sort of shitty and matt will likely mad, but we
        have to use a custom `get_or_create` logic here because
        the validated data isn't the same once you start munging
        the data.
        """
        #
        bill = validated_data.get('bill')
        group = validated_data.get('group')

        queryset = Wrapper.objects.filter(bill=bill, group=group)
        if queryset.count() > 0:
            return queryset.first()
        else:
            return Wrapper.objects.create(**validated_data)
