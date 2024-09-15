# Generated by Django 4.2.16 on 2024-09-14 18:02

from django.db import migrations

import core.fields


class Migration(migrations.Migration):
    dependencies = [
        ("counter", "0021_rename_check_cashregistersummaryitem_is_checked"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="icon",
            field=core.fields.ResizedImageField(
                blank=True,
                height=70,
                force_format="WEBP",
                null=True,
                upload_to="products",
                verbose_name="icon",
            ),
        ),
        migrations.AlterField(
            model_name="producttype",
            name="icon",
            field=core.fields.ResizedImageField(
                blank=True,
                force_format="WEBP",
                height=70,
                null=True,
                upload_to="products",
            ),
        ),
    ]
