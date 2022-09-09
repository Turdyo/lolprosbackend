# Generated by Django 4.1 on 2022-09-08 00:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Team",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=100, null=True)),
                ("logo", models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Player",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="lolpros.team"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Account",
            fields=[
                ("id", models.BigIntegerField(primary_key=True, serialize=False)),
                ("name", models.CharField(blank=True, max_length=20, null=True)),
                ("summonerLvl", models.BigIntegerField(blank=True, null=True)),
                (
                    "profileIcon",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                ("tier", models.CharField(blank=True, max_length=100, null=True)),
                ("rank", models.CharField(blank=True, max_length=100, null=True)),
                ("leaguePoints", models.IntegerField(blank=True, null=True)),
                ("wins", models.IntegerField(blank=True, null=True)),
                ("losses", models.IntegerField(blank=True, null=True)),
                ("LPC", models.IntegerField(blank=True, null=True)),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="lolpros.player"
                    ),
                ),
            ],
        ),
    ]