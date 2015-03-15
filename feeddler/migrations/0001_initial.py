# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('link', models.CharField(default=b'', max_length=512)),
                ('title', models.CharField(max_length=512, null=True, blank=True)),
                ('content', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntryWord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField(default=0)),
                ('entry', models.ForeignKey(to='feeddler.Entry')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('link', models.URLField(unique=True, max_length=512)),
                ('is_active', models.BooleanField(default=False, verbose_name=b'Active')),
                ('title', models.CharField(max_length=1024, null=True, blank=True)),
                ('last_modified', models.DateTimeField(null=True, blank=True)),
                ('etag', models.CharField(max_length=512, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FeedWord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField(default=0)),
                ('feed', models.ForeignKey(to='feeddler.Feed')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('word', models.CharField(max_length=64, serialize=False, primary_key=True)),
                ('count', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='feedword',
            name='word',
            field=models.ForeignKey(to='feeddler.Word'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='feedword',
            unique_together=set([('feed', 'word')]),
        ),
        migrations.AddField(
            model_name='feed',
            name='words',
            field=models.ManyToManyField(to='feeddler.Word', through='feeddler.FeedWord'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entryword',
            name='word',
            field=models.ForeignKey(to='feeddler.Word'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='entryword',
            unique_together=set([('entry', 'word')]),
        ),
        migrations.AddField(
            model_name='entry',
            name='feed',
            field=models.ForeignKey(to='feeddler.Feed'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entry',
            name='words',
            field=models.ManyToManyField(to='feeddler.Word', through='feeddler.EntryWord'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='entry',
            unique_together=set([('feed', 'link')]),
        ),
    ]
