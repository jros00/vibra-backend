# Generated by Django 4.2.16 on 2024-09-19 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_alter_song_artist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='mp3_file',
            field=models.FileField(upload_to='mp3s/'),
        ),
    ]