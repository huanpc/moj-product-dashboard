# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-21 14:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prototype', '0004_auto_20160721_0947'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'permissions': (('adjustmentexport_project', 'Can run Adjustment Export'), ('intercompanyexport_project', 'Can run Intercompany Export'), ('projectdetailexport_project', 'Can run Intercompany Export'))},
        ),
    ]