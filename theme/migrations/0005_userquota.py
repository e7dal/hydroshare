# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('theme', '0004_userprofile_create_irods_user_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserQuota',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('allocated_value', models.BigIntegerField(default=10000)),
                ('used_value', models.BigIntegerField(default=0)),
                ('unit', models.CharField(default=b'MB', max_length=10)),
                ('zone', models.CharField(default=b'hydroshare_internal', max_length=100)),
                ('user', models.ForeignKey(related_name='quotas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User quota',
                'verbose_name_plural': 'User quotas',
            },
        ),
    ]
