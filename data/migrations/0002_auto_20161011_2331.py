# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='completedtorrents',
            name='deletedTime',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='completedtorrents',
            name='emailed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='completedtorrents',
            name='label',
            field=models.CharField(max_length=20, blank=True),
        ),
    ]
