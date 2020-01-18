# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-01-15 14:42
from __future__ import unicode_literals

import django.contrib.postgres.fields
import django.contrib.postgres.fields.hstore
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hs_composite_resource', '0001_initial'),
        ('hs_file_types', '0011_model_program_aggregation'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelInstanceFileMetaData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('extra_metadata', django.contrib.postgres.fields.hstore.HStoreField(default={})),
                ('keywords', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100, null=True), default=[], size=None)),
                ('is_dirty', models.BooleanField(default=False)),
                ('has_model_output', models.BooleanField(default=False)),
                ('metadata_json', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('executed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='model_instances', to='hs_file_types.ModelProgramLogicalFile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ModelInstanceLogicalFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset_name', models.CharField(blank=True, max_length=255, null=True)),
                ('extra_data', django.contrib.postgres.fields.hstore.HStoreField(default={})),
                ('folder', models.CharField(blank=True, max_length=4096, null=True)),
                ('model_instance_type', models.CharField(default=b'Unknown Model Instance', max_length=255)),
                ('metadata', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='logical_file', to='hs_file_types.ModelInstanceFileMetaData')),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hs_composite_resource.CompositeResource')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
