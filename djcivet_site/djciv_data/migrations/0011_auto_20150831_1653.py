# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djciv_data', '0010_text_textdelete'),
    ]

    operations = [
        migrations.AlterField(
            model_name='text',
            name='textdelete',
            field=models.BooleanField(),
        ),
    ]
