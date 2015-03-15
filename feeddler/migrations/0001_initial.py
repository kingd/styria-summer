# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('link', models.URLField(unique=True, max_length=512)),
                ('is_active', models.BooleanField(default=False, verbose_name=b'Active')),
                ('title', models.CharField(max_length=1024, null=True, editable=False, blank=True)),
                ('last_build_date', models.DateTimeField(null=True, editable=False, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
