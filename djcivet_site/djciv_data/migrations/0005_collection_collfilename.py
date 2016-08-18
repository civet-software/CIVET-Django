# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djciv_data', '0004_auto_20150615_1637'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='collfilename',
            field=models.CharField(default=2, max_length=100),
            preserve_default=False,
        ),
    ]
