from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organizations', '0003_auto_20170609_0749'),
        ('groups', '0003_auto_20170623_0759'),
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
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.User')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.Organization', db_constraint=False, null=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groups.Group', db_constraint=False, null=True)),
            ],
            options={
                'verbose_name_plural': 'alert',
                'verbose_name': 'alert',
                'abstract': False,
            },
        ),
    ]
