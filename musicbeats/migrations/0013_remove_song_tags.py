# Generated by Django 4.0.3 on 2022-04-24 15:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('musicbeats', '0012_song_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='song',
            name='tags',
        ),
    ]