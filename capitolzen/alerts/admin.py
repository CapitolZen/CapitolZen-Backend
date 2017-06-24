from django.contrib import admin
from .models import Alerts


class AlertsAdmin:
    list_display = ['message']

admin.site.register(Alerts)

