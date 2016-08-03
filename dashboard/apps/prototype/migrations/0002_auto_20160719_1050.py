# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-19 10:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prototype', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='staff_number',
            field=models.PositiveSmallIntegerField(null=True, unique=True),
        ),
        migrations.AddField(
            model_name='project',
            name='hr_id',
            field=models.CharField(max_length=12, null=True, unique=True),
        ),
    ]
