# Generated by Django 4.2.16 on 2024-10-06 14:52

from django.db import migrations

import core.models


class Migration(migrations.Migration):
    dependencies = [("core", "0038_alter_preferences_receive_weekmail")]

    operations = [
        migrations.AlterModelManagers(
            name="user", managers=[("objects", core.models.CustomUserManager())]
        )
    ]
