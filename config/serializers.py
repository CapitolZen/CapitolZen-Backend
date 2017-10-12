from rest_framework import serializers
from urllib.parse import urlparse
from django.conf import settings
from capitolzen.utils.s3 import copy_s3_object


class RemoteFileField(serializers.Field):
    """
    Returns the full url to whatever file exists.

    If a url is provided, we move it to the proper location for storage.

    I think this whole thing is pretty questionable.
    """

    def _parse_incoming_file_data(self, data):
        """
        Incoming data is going to be some sort of URL.
        :param data:
        :return:
        """

        url = urlparse(data)

        if '.s3.amazonaws.com' in url.netloc:
            bucket = url.netloc.replace('.s3.amazonaws.com', '')
            if bucket in [settings.AWS_TEMP_BUCKET_NAME, settings.AWS_BUCKET_NAME]:
                mode = 's3'
                file = url.path[1:]
            else:
                raise serializers.ValidationError("We only support files being uploaded from our buckets.")
        else:
            raise serializers.ValidationError("We do not support non-s3 uploads. at this time")

        return {
            'mode': mode,
            'file': file,
            'bucket': bucket,
        }

    def get_attribute(self, obj):
        return obj

    def to_representation(self, obj):
        attr = getattr(obj, self.field_name)

        if attr:
            return attr.url

        return None

    def to_internal_value(self, data):
        if not data:
            return None

        info = self._parse_incoming_file_data(data)

        instance = self.parent.instance
        attr = getattr(instance, self.field_name)

        # Don't do anything if it's the same file
        if attr and attr.file.name and attr.file.name == info['file']:
            return attr.file.name

        source = {
            'key': info['file'],
            'bucket': info['bucket'],
        }

        destination = {
            'key': None,
            'bucket': settings.AWS_BUCKET_NAME
        }

        if attr.field.upload_to:
            destination['key'] = attr.field.upload_to(instance, info['file'])
        else:
            destination['key'] = info['file']

        # Don't copy if the file is already in the correct location
        if source != destination:
            copy_s3_object(source, destination, delete_source=True)

        return destination['key']


