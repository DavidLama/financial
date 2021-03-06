# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-06-03 15:15
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payoff', '0004_banktransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='payoff',
            name='bank_fee',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(
                0.0), django.core.validators.MaxValueValidator(9999999.999)], verbose_name='bank fee'),
        ),
    ]
