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


class DocManager:
    def __init__(self, org_instance):
        self.organization = org_instance
        client = aws_client(service='s3')
        self.client = client()
        self.bucket = settings.AWS_BUCKET_NAME

    def upload_logo(self):
        key = "%s/organization/assets/" % self.organization.id
        conditions = [
            {'acl': 'public-read'},
            {'starts-with', '$key', key}
        ]

        url = self.client.generate_presigned_post(
            Bucket=self.bucket,
            Conditions=conditions
        )

        return url

    def upload_asset(self, group_id=False):
        if not group_id:
            key = "%s/uploads/" % self.organization.id
            conditions = [
                {'acl': 'public-read'},
                {'starts-with', '$key', key}
            ]
        else:
            key = "%s/%s/uploads/" % (self.organization.id, group_id)
            conditions = [
                {'acl': 'public-read'},
                {'starts-with', '$key', key}
            ]
        url = self.client.generate_presigned_post(
            Bucket=self.bucket,
            Conditions=conditions
        )
        return url
