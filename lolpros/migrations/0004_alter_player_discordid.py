# Generated by Django 4.1 on 2022-09-25 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lolpros", "0003_remove_team_test"),
    ]

    operations = [
        migrations.AlterField(
            model_name="player",
            name="discordId",
            field=models.BigIntegerField(primary_key=True, serialize=False),
        ),
    ]
