# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djciv_data', '0006_auto_20150616_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='text',
            name='textbiblio',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='text',
            name='textgeogloc',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
