# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-18 11:05
from __future__ import unicode_literals

from django.db import migrations
from capitolzen.organizations.utils import get_stripe_client
from django.conf import settings


def forwards(apps, schema_editor):
    if settings.STRIPE_ENABLE_SYNC:
        stripe = get_stripe_client()
        has_more = True
        customers = stripe.Customer.list()
        total_customers = 0
        while has_more:
            last_customer_id = None
            has_more = customers.has_more
            for customer in customers.data:
                last_customer_id = customer.id
                total_customers += 1

                if not customer.subscriptions.data or customer.subscriptions.data[0].plan.id != "basic":
                    customer.delete()

            if has_more:
                customers = stripe.Customer.list(starting_after=last_customer_id)

        print("Total Customers: %s" % total_customers)


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0020_auto_20180117_1913'),
    ]

    operations = [
        migrations.RunPython(forwards),
    ]
