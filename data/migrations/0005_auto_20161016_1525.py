# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0004_remove_completedtorrents_deletedtime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='completedtorrents',
            name='hash',
            field=models.CharField(max_length=40, serialize=False, primary_key=True),
        ),
    ]
