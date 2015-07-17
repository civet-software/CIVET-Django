# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djciv_data', '0003_auto_20150605_2048'),
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('caseparent', models.CharField(max_length=100, blank=True)),
                ('caseid', models.CharField(max_length=100)),
                ('casedate', models.DateTimeField()),
                ('casecoder', models.CharField(max_length=32)),
                ('casecmt', models.CharField(max_length=255, blank=True)),
                ('casevalues', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='text',
            name='textmkupdate',
            field=models.DateTimeField(),
        ),
    ]
