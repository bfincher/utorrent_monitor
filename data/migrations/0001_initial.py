# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CompletedTorrents',
            fields=[
                ('hash', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
    ]
