# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-04 13:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prototype', '0008_client_visible'),
    ]

    operations = [
        migrations.CreateModel(
            name='Saving',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('name', models.CharField(max_length=128, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'One off'), (2, 'Monthly'), (3, 'Annually')], default=1)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='savings', to='prototype.Project')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]