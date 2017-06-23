from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Alerts',
            fields=[
                ('message', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='Message')),
            ],
            options={
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
                'abstract': False,
            },
        ),
    ]
