# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djciv_data', '0009_auto_20150827_2015'),
    ]

    operations = [
        migrations.AddField(
            model_name='text',
            name='textdelete',
            field=models.BooleanField(default=False),
        ),
    ]
