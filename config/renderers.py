from django.conf import settings
from rest_framework_swagger.renderers import OpenAPIRenderer


class DocRenderer(OpenAPIRenderer):

    def get_customizations(self):
        """
        Adds settings, overrides, etc. to the specification.
        """
        return {
            "host": settings.SWAGGER_HOST,
            "schemes": ['https'],
            "securityDefinitions": (
                settings.SWAGGER_SETTINGS['SECURITY_DEFINITIONS']
            ),
            "security": [{ settings.SWAGGER_SETTINGS['SECURITY'] : [] }]
        }

