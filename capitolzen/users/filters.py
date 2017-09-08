from dry_rest_permissions.generics import DRYPermissionFiltersBase
from rest_framework.exceptions import NotAuthenticated


class ResourceOwnerFilterBackend(DRYPermissionFiltersBase):
    def filter_list_queryset(self, request, queryset, view):
        if request.user.is_anonymous():
            raise NotAuthenticated()
        else:
            return queryset.filter(owner=request.user)
