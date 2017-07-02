from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid
from capitolzen.users.models import User


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Alerts',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('message', models.TextField(auto_created=True, serialize=False, verbose_name='message')),
                ('user', models.TextField(auto_created=True, serialize=False, verbose_name='user')),
                ('organization', models.TextField(auto_created=True, serialize=False, verbose_name='user')),
                ('group', models.TextField(auto_created=True, serialize=False, verbose_name='user')),
            ],
            options={
                'verbose_name_plural': 'alert',
                'verbose_name': 'alert',
                'abstract': False,
            },
        ),
    ]
