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
        self.client = aws_client('s3')
        self.bucket = settings.AWS_BUCKET_NAME

    def upload_logo(self):
        key = "%s/organization/assets/" % self.organization.id
        conditions = [
            {'acl': 'public-read'},
            {'success_action_status': '201'}
        ]
        data = self.client.generate_presigned_post(
            Bucket=self.bucket,
            Key=key,
            Conditions=conditions
        )
        return data

    def upload_asset(self, file, acl=False, group_id=False):
        if not group_id:
            key = "%s/uploads/%s" % (self.organization.id, file)
        else:
            key = "%s/%s/uploads/%s" % (self.organization.id, group_id, file)

        if not acl:
            acl = 'public-read'

        conditions = [
            {'acl': acl},
            {'success_action_status': '201'}
        ]
        data = self.client.generate_presigned_post(
            Bucket=self.bucket,
            Key=key,
            Conditions=conditions
        )
        return data
