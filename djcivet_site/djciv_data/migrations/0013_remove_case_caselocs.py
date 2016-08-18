# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djciv_data', '0012_case_caselocs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='case',
            name='caselocs',
        ),
    ]
