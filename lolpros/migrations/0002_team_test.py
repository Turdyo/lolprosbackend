# Generated by Django 4.1 on 2022-09-25 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lolpros", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="test",
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
