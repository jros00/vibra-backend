# Generated by Django 5.1.1 on 2024-09-29 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='album_image_dominant_color',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='track',
            name='album_image_palette',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
