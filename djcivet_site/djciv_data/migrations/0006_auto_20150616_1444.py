# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djciv_data', '0005_collection_collfilename'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='collfilename',
            field=models.CharField(max_length=100, blank=True),
        ),
    ]
