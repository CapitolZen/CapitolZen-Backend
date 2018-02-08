from dry_rest_permissions.generics import allow_staff_or_superuser, authenticated_users


class MixinExternalData:
    """
    A mixin to set permissions and various other common
    functionality for data created from external data sources
    """

    @staticmethod
    @authenticated_users
    def has_read_permission(request):
        return True

    @authenticated_users
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        return False
