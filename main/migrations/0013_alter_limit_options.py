# Generated by Django 4.0.5 on 2022-09-28 12:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_alter_teamparticapation_particapants'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='limit',
            options={'ordering': ['id'], 'verbose_name': 'Лимит', 'verbose_name_plural': 'Лимиты'},
        ),
    ]
