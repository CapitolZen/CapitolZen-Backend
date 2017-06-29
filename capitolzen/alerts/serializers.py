from rest_framework_json_api import serializers
from .models import Alerts


class AlertsSerializer(serializers.ModelSerializer):


    class Meta:
        model = Alerts
        fields = ('message',)
        lookup_field = 'message'

    def create(self, validated_data):
        message = super().create(validated_data)
        message.set_password(validated_data['password'])
        message.save()
        return message
