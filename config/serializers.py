from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    """
    Deprecated: new serializers should use BaseModelMetaSerializer
    """

    id = serializers.UUIDField(
        read_only=True,
        help_text="Unique UUID based identifier that can be used to access "
                  "the resource."
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
    metadata = serializers.JSONField(
        required=False, allow_null=True, default=None,
        help_text="Meta is provided for your use, you can put any "
                  "JSON formatted string in here and we'll store it off so "
                  "that you can use it to track metadata associated with the "
                  "given resource instance."
    )
