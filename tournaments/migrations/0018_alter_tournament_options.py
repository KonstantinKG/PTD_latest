# Generated by Django 4.0.5 on 2022-10-07 09:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0017_status_priority'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tournament',
            options={'ordering': ['date_start', 'date_end', 'status__priority'], 'verbose_name': 'Турнир', 'verbose_name_plural': 'Турниры'},
        ),
    ]
