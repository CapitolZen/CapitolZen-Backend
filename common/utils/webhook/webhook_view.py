from json import loads
import logging

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

logger = logging.getLogger('app')


class WebhookAPI(APIView):
    # Define a tuple of handlers that this webhook should support
    # Ordering can matter so please ensure the handlers you want used first
    # are put at the front of the tuple.
    handlers = None

    # Add Serializer Class validate data
    serializer = None
    def post(self, request):
        logger.info("Received webhook")

        # We should really be doing these determinations in a serializer
        if self.serializer:
            payload = self.serializer(data=request.body).data
        else:
            payload = loads(request.body)

        if not payload:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Unsupported Payload"
                }, status=status.HTTP_400_BAD_REQUEST
            )

        for handler in self.handlers:
            if handler().digest(payload):
                # If we find something that can handle this request, stop
                # looking for additional handlers
                logger.info("Handled Webhook")
                return Response(
                    {
                        'message': 'Accepted Request',
                        'status': status.HTTP_200_OK
                    }
                )
        else:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "No Handler Defined"
                }, status=status.HTTP_400_BAD_REQUEST
            )
