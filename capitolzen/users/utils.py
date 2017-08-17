from django.conf import settings
from intercom.client import Client


def get_intercom_client():
    """
    Init the client and automatically add in the access token.
    :return:
    """
    return Client(personal_access_token=settings.INTERCOM_ACCESS_TOKEN)
