# Generated by Django 1.11.13 on 2018-10-18 23:15
from __future__ import unicode_literals

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("counter", "0016_producttype_comment")]

    operations = [
        migrations.CreateModel(
            name="StudentCard",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uid",
                    models.CharField(
                        max_length=14,
                        unique=True,
                        validators=[django.core.validators.MinLengthValidator(4)],
                        verbose_name="uid",
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_cards",
                        to="counter.Customer",
                        verbose_name="student cards",
                    ),
                ),
            ],
        )
    ]
