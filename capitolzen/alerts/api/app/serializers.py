from rest_framework_json_api import serializers
from capitolzen.alerts.models import Alerts


class AlertsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alerts
        fields = ('id', 'message', 'is_read', 'created', 'user', 'organization', 'group')

    id = serializers.ReadOnlyField()
