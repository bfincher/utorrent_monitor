# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_auto_20161011_2331'),
    ]

    operations = [
        migrations.AddField(
            model_name='completedtorrents',
            name='status',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
    ]
