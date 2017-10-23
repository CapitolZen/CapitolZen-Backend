from django.contrib import admin

from capitolzen.organizations.models import (
    Organization, OrganizationUser, OrganizationOwner, OrganizationInvite
)


class OwnerInline(admin.StackedInline):
    model = OrganizationOwner
    raw_id_fields = ('organization_user',)


class UserInline(admin.StackedInline):
    model = OrganizationUser
    raw_id_fields = ('organization',)


class OrganizationAdmin(admin.ModelAdmin):
    inlines = [OwnerInline, UserInline]
    list_display = ['name', 'is_active']
    search_fields = ['name']
    list_filter = ('is_active',)


class OrganizationUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'is_admin']
    raw_id_fields = ('user', 'organization')


class OrganizationOwnerAdmin(admin.ModelAdmin):
    raw_id_fields = ('organization_user', 'organization')


class OrganizationInviteAdmin(admin.ModelAdmin):
    list_display = ['email', 'status', 'organization', 'created', 'modified']
    search_fields = ['email', 'status', 'organization']
    list_filter = ('status', 'organization')


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationInvite, OrganizationInviteAdmin)
