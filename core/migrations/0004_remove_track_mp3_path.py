# Generated by Django 4.2.16 on 2024-09-21 22:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_track_mp3_path'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='track',
            name='mp3_path',
        ),
    ]
