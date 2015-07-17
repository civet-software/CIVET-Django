# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djciv_data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('collid', models.CharField(max_length=100)),
                ('colldate', models.DateField()),
                ('colledit', models.DateTimeField()),
                ('collcmt', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Text',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('textid', models.CharField(max_length=100)),
                ('textdate', models.DateField()),
                ('textpublisher', models.CharField(max_length=100)),
                ('textpubid', models.CharField(max_length=100)),
                ('textlicense', models.CharField(max_length=100)),
                ('textlede', models.CharField(max_length=100)),
                ('textoriginal', models.TextField()),
                ('textmkup', models.TextField()),
                ('textmkupdate', models.DateField()),
                ('textmkupcoder', models.CharField(max_length=32)),
            ],
        ),
        migrations.RemoveField(
            model_name='choice',
            name='question',
        ),
        migrations.DeleteModel(
            name='Choice',
        ),
        migrations.DeleteModel(
            name='Question',
        ),
    ]
