# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djciv_data', '0008_auto_20150827_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='casecmt',
            field=models.CharField(max_length=500, blank=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='collcmt',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='text',
            name='textcmt',
            field=models.CharField(max_length=500, blank=True),
        ),
    ]
