from django.contrib import admin
from .models import Bill, Wrapper
from config.admin import BaseModelAdmin


class BillAdmin(BaseModelAdmin):
    list_display = [
        'state',
        'current_committee',
        'sponsor',
        'title',
        'state_id',
        'categories',
        'id'
    ]


class WrapperAdmin(BaseModelAdmin):
    list_display = ['organization', 'bill', 'group', 'notes', 'position']


admin.site.register(Bill, BillAdmin)
admin.site.register(Wrapper, WrapperAdmin)
