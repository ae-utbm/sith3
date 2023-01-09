# Generated by Django 3.2.16 on 2023-01-08 12:49

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ("counter", "0018_producttype_priority"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="producttype",
            options={"ordering": ["-priority", "name"], "verbose_name": "product type"},
        ),
        migrations.CreateModel(
            name="BillingInfo",
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
                    "first_name",
                    models.CharField(max_length=22, verbose_name="First name"),
                ),
                (
                    "last_name",
                    models.CharField(max_length=22, verbose_name="Last name"),
                ),
                (
                    "address_1",
                    models.CharField(max_length=50, verbose_name="Address 1"),
                ),
                (
                    "address_2",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="Address 2"
                    ),
                ),
                ("zip_code", models.CharField(max_length=16, verbose_name="Zip code")),
                ("city", models.CharField(max_length=50, verbose_name="City")),
                ("country", django_countries.fields.CountryField(max_length=2)),
                (
                    "customer",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="billing_infos",
                        to="counter.customer",
                    ),
                ),
            ],
        ),
    ]
