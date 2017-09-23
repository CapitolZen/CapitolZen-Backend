from rest_framework import serializers
from django.conf import settings


class BaseSerializer(serializers.Serializer):
    """
    Deprecated: new serializers should use BaseModelMetaSerializer
    """

    id = serializers.UUIDField(
        read_only=True,
        help_text="Unique UUID4 based identifier that can be used to access "
                  "the resource."
    )
    type = serializers.SerializerMethodField(
        help_text="Identifies the resource that the JSON object represents. "
                  "This will be an all lowercase representation of the "
                  "resource name."
    )
    created = serializers.DateTimeField(
        format='iso-8601',
        read_only=True,
        help_text="ISO 8601 formatted timestamp identifying when the object "
                  "was created in the database."
    )
    modified = serializers.DateTimeField(
        format='iso-8601',
        read_only=True,
        help_text="ISO 8601 formatted timestamp identifying when the object "
                  "was last modified."
    )

    def update(self, instance, validated_data):
        return instance


class BaseMetaSerializer(BaseSerializer):
    """
    Deprecated: new serializers should use BaseModelMetaSerializer
    """

    meta = serializers.JSONField(
        required=False, allow_null=True, default=None,
        help_text="Meta is provided for your use, you can put any "
                  "JSON formatted string in here and we'll store it off so "
                  "that you can use it to track metadata associated with the "
                  "given resource instance."
    )


class BaseModelMetaSerializer(serializers.ModelSerializer):
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
    type = serializers.SerializerMethodField(
        help_text="Identifies the resource that the JSON object represents. "
                  "This will be an all lowercase representation of the "
                  "resource name."
    )
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
    meta = serializers.JSONField(
        required=False, allow_null=True, default=None,
        help_text="Meta is provided for your use, you can put any "
                  "JSON formatted string in here and we'll store it off so "
                  "that you can use it to track metadata associated with the "
                  "given resource instance."
    )

    def get_type(self, obj):
        return obj.__class__.__name__.lower()


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