# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-05 13:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FlightLog', '0006_plannedflight_gnd_activity'),
    ]

    operations = [
        migrations.AddField(
            model_name='plannedflight',
            name='iCalUID',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]