# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-02 10:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prototype', '0005_auto_20160721_1455'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('projects', models.ManyToManyField(related_name='project_groups', to='prototype.Project')),
            ],
        ),
    ]
