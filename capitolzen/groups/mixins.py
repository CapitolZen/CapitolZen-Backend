from dry_rest_permissions.generics import allow_staff_or_superuser

class MixinResourceModifiedByPage(object):

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        if request.user.is_anonymous():
            page = getattr(request, 'page', None)
            if not page:
                return False

            if page.allow_anon:
                return True

        return self.organization.is_member(request.user)

