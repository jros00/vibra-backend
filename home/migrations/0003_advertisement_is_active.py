# Generated by Django 4.2.16 on 2024-09-19 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='advertisement',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
