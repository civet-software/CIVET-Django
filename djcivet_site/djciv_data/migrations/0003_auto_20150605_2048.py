# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djciv_data', '0002_auto_20150605_1832'),
    ]

    operations = [
        migrations.AddField(
            model_name='text',
            name='textcmt',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='text',
            name='textparent',
            field=models.CharField(max_length=100, blank=True),
        ),
    ]
