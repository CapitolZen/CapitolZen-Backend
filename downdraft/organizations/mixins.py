from crum import get_current_user
from dry_rest_permissions.generics import allow_staff_or_superuser


class MixinResourcedOwnedByOrganization:
    """
    A model mixin useful for automatically setting some DRY Permissions.

    -- Only members of the organization can CRUD
    -- All Members of the organization can CRUD
    """

    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(request):
        return True

    @staticmethod
    def has_create_permission(request):
        return True

    def has_object_read_permission(self, request):
        if not hasattr(self, 'organization'):
            return False

        return self.organization.is_member(request.user)

    def has_object_write_permission(self, request):
        if not hasattr(self, 'organization'):
            return False

        return self.organization.is_member(request.user)

    def has_object_create_permission(self, request):
        if not hasattr(self, 'organization'):
            return False

        return self.organization.is_member(request.user)
