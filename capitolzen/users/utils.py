from django.conf import settings
from intercom.client import Client
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


def get_intercom_client():
    """
    Init the client and automatically add in the access token.
    :return:
    """
    return Client(personal_access_token=settings.INTERCOM_ACCESS_TOKEN)


def token_encode(user, **extra_data):
    payload = jwt_payload_handler(user)
    payload = {**payload, **extra_data}
    return jwt_encode_handler(payload)


def token_decode(token):
    return jwt_decode_handler(token)
