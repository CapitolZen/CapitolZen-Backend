from django.contrib import admin
from .models import Bill, Wrapper


class BillAdmin(admin.ModelAdmin):
    list_display = ['state', 'status', 'committee', 'sponsor', 'title', 'state_id', 'categories']


class WrapperAdmin(admin.ModelAdmin):
    list_display = ['organization', 'bill', 'groups', 'notes']

admin.site.register(Bill, BillAdmin)
admin.site.register(Wrapper, WrapperAdmin)
