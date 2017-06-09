from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField

from .models import Bill, Wrapper


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = ('id',)


class WrapperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wrapper
        fields = ('id',)

    organization = ResourceRelatedField(
        many=False,
        read_only=True,
        source='organizations_organization'
    )

    bill = ResourceRelatedField(
        many=False,
        source='proposals_bill'
    )
