# Generated by Django 4.0.5 on 2022-09-23 17:17

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_alter_teamparticapation_particapants'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teamparticapation',
            name='particapants',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, verbose_name='Участники'),
        ),
    ]
