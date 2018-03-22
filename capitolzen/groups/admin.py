from django.contrib import admin
from .models import Group, Report, File


class GroupAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'description',
        'organization',
        'created',
        'modified'
    ]
    search_fields = ['title', 'description', 'organization']

class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'group', 'user']


class FileAdmin(admin.ModelAdmin):
    list_display = ['name', 'created', 'modified']


admin.site.register(Group, GroupAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(File, FileAdmin)
