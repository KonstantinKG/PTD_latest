# Generated by Django 4.0.5 on 2022-09-20 03:12

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tournaments', '0008_tournamentassociationteams_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tournament',
            name='teams',
        ),
        migrations.AlterField(
            model_name='tournament',
            name='players',
            field=models.ManyToManyField(blank=True, related_name='self', to=settings.AUTH_USER_MODEL, verbose_name='Учавствующие игроки'),
        ),
    ]
