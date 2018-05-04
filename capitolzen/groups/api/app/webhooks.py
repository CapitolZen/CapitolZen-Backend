from common.utils.webhook.webhook_view import WebhookAPI
from capitolzen.groups.models import File
import logging
from rest_framework.permissions import AllowAny



logger = logging.getLogger('app')


class FilePreviewHanlder(object):
    def digest(self, data):
        if not data.get('id', False):
            return True
        try:
            file = File.objects.get(metadata__preview__id=data["id"])
            file.set_preview(data)
            return True
        except Exception:
            logger.warning('no file found')
            return True


class FilePreviewWebhook(WebhookAPI):
    permission_classes = (AllowAny,)
    handlers = (FilePreviewHanlder,)
