from rest_framework import serializers
from django.conf import settings


class BaseModelSerializer(serializers.ModelSerializer):
    """
    Instead of using serializers.Serializer, this uses ModelSerializer,
    which allows us to take advantage of some of the built in DRF
    functionality, mainly around CRUD actions.
    """
    id = serializers.UUIDField(
        read_only=True,
        help_text="Unique UUID4 based identifier that can be used to access "
                  "the resource."
    )


class BaseInternalModelSerializer(BaseModelSerializer):
    """
    Instead of using serializers.Serializer, this uses ModelSerializer,
    which allows us to take advantage of some of the built in DRF
    functionality, mainly around CRUD actions.
    """
    created = serializers.DateTimeField(
        format=settings.API_DATETIME_FORMAT,
        read_only=True,
        help_text="ISO 8601 formatted timestamp identifying when the object "
                  "was created in the database."
    )
    modified = serializers.DateTimeField(
        format=settings.API_DATETIME_FORMAT,
        read_only=True,
        help_text="ISO 8601 formatted timestamp identifying when the object "
                  "was last modified."
    )


class NoByteCharField(serializers.CharField):
    def to_internal_value(self, data):
        data = data.replace(
            '\\0x00', '').replace(
            '\0x00', '').replace(
            '0x00', '').replace(
            '\0', '').replace(
            '\x00', '').replace(
            '0x04', '')

        return super(NoByteCharField, self).to_internal_value(data)