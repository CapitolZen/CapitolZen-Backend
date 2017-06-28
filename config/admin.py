from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from config.widgets import JSONEditorWidget


class BaseModelAdmin(admin.ModelAdmin):

    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }
