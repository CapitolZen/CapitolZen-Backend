from boto3 import client
from django.conf import settings


def aws_client(service='lambda'):
    bclient = client(
                    service,
                    aws_access_key_id=settings.AWS_ACCESS_ID,
                    aws_secret_access_key=settings.AWS_SECRET_KEY,
                    region_name=settings.AWS_REGION
                    )

    return bclient