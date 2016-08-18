# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djciv_data', '0007_auto_20150827_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='collcmt',
            field=models.CharField(max_length=255),
        ),
    ]
