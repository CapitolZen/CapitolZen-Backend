from django.contrib import admin
from .models import Group, Comment


class GroupAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'organization', 'created', 'modified']
    search_fields = ['title', 'description', 'organization']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'text']

admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
