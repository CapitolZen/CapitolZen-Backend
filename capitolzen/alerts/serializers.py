from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework.validators import UniqueValidator
from .models import Alerts


class AlertsSerializer(serializers.ModelSerializer):

    # username = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = Alerts
        fields = ('message',)
        # read_only_fields = ('id', 'user_is_staff', 'user_is_admin', 'organizations')
        lookup_field = 'message'

    def create(self, validated_data):
        mes = super().create(validated_data)
        mes.set_password(validated_data['password'])
        mes.save()
        return mes
