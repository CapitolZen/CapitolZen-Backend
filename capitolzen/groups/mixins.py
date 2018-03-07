from rest_framework_jwt.settings import api_settings
from django.db import models
from dry_rest_permissions.generics import allow_staff_or_superuser
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


class MixinResourceOwnedByPage(object):

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        print(request.__dict__)
        if self.page.visibility == 'anyone':
            return True

        if request.organization == self.page.group.organization:
            return True

        return True
