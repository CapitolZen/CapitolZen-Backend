import boto3
import json
from django.conf import settings
from botocore.exceptions import ClientError
from logging import getLogger

logger = getLogger('app')


def get_s3_client():
    """
    Init the s3 boto client with our unique settings.
    :return:
    """
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_ID,
        aws_secret_access_key=settings.AWS_SECRET_KEY)


def get_s3_resource():
    """
    :return:
    """
    return boto3.resource(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_ID,
        aws_secret_access_key=settings.AWS_SECRET_KEY)


def copy_s3_object(source,
                   destination,
                   delete_source=False,
                   raise_exceptions=False):
    """
    :param source: {'bucket': <bucket>, 'key': <key>}
    :param destination: {'bucket': <bucket>, 'key': <key>}
    :param delete_source: Delete source after copy
    :param raise_exceptions: Raise exceptions if
            file cannot be found or whatever
    :return:
    """

    s3_resource = get_s3_resource()

    try:
        s3_resource.Object(destination['bucket'], destination['key']) \
            .copy_from(CopySource='%s/%s' % (source['bucket'], source['key']))

        if delete_source:
            s3_resource.Object(source['bucket'], source['key']).delete()

    except ClientError as e:
        logger.info(json.dumps(e.__dict__))
        if raise_exceptions:
            raise ValueError('error occurred during copy_s3_object')


def generate_s3_url(key, bucket=settings.AWS_BUCKET_NAME):
    s3 = get_s3_client()
    return s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket,
            'Key': key
        }
    )
