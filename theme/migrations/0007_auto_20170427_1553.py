# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0006_auto_20170309_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='message_end_date',
            field=models.DateField(help_text='Date on which the message will no more be displayed', null=True),
        ),
        migrations.AddField(
            model_name='homepage',
            name='message_start_date',
            field=models.DateField(help_text='Date from which the message will be displayed', null=True),
        ),
        migrations.AddField(
            model_name='homepage',
            name='message_type',
            field=models.CharField(default='Information', max_length=100, choices=[('warning', 'Warning'), ('information', 'Information')]),
        ),
        migrations.AddField(
            model_name='homepage',
            name='show_message',
            field=models.BooleanField(default=False, help_text='Check to show message'),
        ),
    ]
