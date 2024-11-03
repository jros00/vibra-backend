# Generated by Django 4.2.16 on 2024-11-03 13:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('profile2', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TasteProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('color_code', models.CharField(max_length=7)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='taste_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
