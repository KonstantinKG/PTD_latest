# Generated by Django 4.0.5 on 2022-09-21 07:56

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_remove_teams_tournaments_teamparticapation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teamparticapation',
            name='particapants',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Участники'),
        ),
    ]
