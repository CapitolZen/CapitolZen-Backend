from rest_framework import permissions
from rest_framework.generics import get_object_or_404


class IsOwnerOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if (obj.owner_username == request.user.username or
                request.user.is_staff):
            return True
        else:
            return False


class IsSelfOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.username == request.user.username


class IsAnonCreateReadOnlyOrIsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == "POST" and not request.user.is_authenticated():
            return True
        elif not request.user.is_authenticated() and request.method != "POST":
            return False
        elif request.method in permissions.SAFE_METHODS:
            return True

        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated():
            return False
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.username == request.user.username


class IsUserOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.user == request.user or request.user.is_staff:
            return True
        else:
            return False


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff


def check_permissions(func):
    def decorator(self, request, **kwargs):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(self.get_queryset(), **filter_kwargs)
        self.check_object_permissions(self.request, obj)

        return func(self, request, **kwargs)

    return decorator
