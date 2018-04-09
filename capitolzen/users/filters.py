from dry_rest_permissions.generics import DRYPermissionFiltersBase
from rest_framework.exceptions import NotAuthenticated


class ResourceOwnerFilterBackend(DRYPermissionFiltersBase):
    def filter_list_queryset(self, request, queryset, view):
        if request.user.is_anonymous():
            page = getattr(request, 'page', False)
            if not page or not page.allow_anon:
                raise NotAuthenticated()
            if page.allow_anon:
                return queryset
        else:
            return queryset.filter(organization__users=request.user)
