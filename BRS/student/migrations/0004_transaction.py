# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-02-25 17:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0003_bt_map_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='transaction',
            fields=[
                ('transaction_id', models.IntegerField(primary_key=True, serialize=False)),
                ('DATE', models.DateField()),
                ('barcode', models.CharField(max_length=9)),
                ('cardnumber', models.CharField(max_length=14)),
                ('Name', models.CharField(max_length=39)),
                ('branchcode', models.CharField(max_length=4)),
            ],
            options={
                'db_table': 'transaction',
                'managed': False,
            },
        ),
    ]