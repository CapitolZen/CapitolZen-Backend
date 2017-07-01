from django.contrib import admin
from .models import Alerts
from config.admin import BaseModelAdmin


class AlertsAdmin(BaseModelAdmin):
    list_display = ['message']

admin.site.register(Alerts, AlertsAdmin)

