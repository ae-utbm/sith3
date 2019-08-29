# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-31 18:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("subscription", "0007_auto_20180706_1135")]

    operations = [
        migrations.AlterField(
            model_name="subscription",
            name="subscription_type",
            field=models.CharField(
                choices=[
                    ("amicale/doceo", "Amicale/DOCEO member"),
                    ("assidu", "Assidu member"),
                    ("benevoles-euroks", "Eurok's volunteer"),
                    ("crous", "CROUS member"),
                    ("cursus-alternant", "Alternating cursus"),
                    ("cursus-branche", "Branch cursus"),
                    ("cursus-tronc-commun", "Common core cursus"),
                    ("deux-mois-essai", "Two month for free"),
                    ("deux-semestres", "Two semesters"),
                    ("membre-honoraire", "Honorary member"),
                    ("reseau-ut", "UT network member"),
                    ("sbarro/esta", "Sbarro/ESTA member"),
                    ("six-semaines-essai", "Six weeks for free"),
                    ("un-semestre", "One semester"),
                    ("un-semestre-welcome", "One semester Welcome Week"),
                ],
                max_length=255,
                verbose_name="subscription type",
            ),
        )
    ]