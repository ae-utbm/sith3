from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("subscription", "0004_auto_20170821_1849")]

    operations = [
        migrations.AlterField(
            model_name="subscription",
            name="subscription_type",
            field=models.CharField(
                choices=[
                    ("amicale/doceo", "Amicale/DOCEO member"),
                    ("assidu", "Assidu member"),
                    ("crous", "CROUS member"),
                    ("cursus-alternant", "Alternating cursus"),
                    ("cursus-branche", "Branch cursus"),
                    ("cursus-tronc-commun", "Common core cursus"),
                    ("deux-semestres", "Two semesters"),
                    ("membre-honoraire", "Honorary member"),
                    ("reseau-ut", "UT network member"),
                    ("sbarro/esta", "Sbarro/ESTA member"),
                    ("un-semestre", "One semester"),
                    ("un-semestre-welcome", "One semester Welcome Week"),
                ],
                max_length=255,
                verbose_name="subscription type",
            ),
        )
    ]
