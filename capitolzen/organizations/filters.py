from dry_rest_permissions.generics import DRYPermissionFiltersBase
from rest_framework.exceptions import NotAuthenticated


class FilterOnActiveOrganization(DRYPermissionFiltersBase):
    def filter_list_queryset(self, request, queryset, view):

        if request.user.is_authenticated:
            if hasattr(request, 'organization') and request.organization:
                return queryset.filter(organization=request.organization)

        return queryset
