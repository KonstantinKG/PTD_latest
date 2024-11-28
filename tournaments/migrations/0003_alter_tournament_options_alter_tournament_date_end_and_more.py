# Generated by Django 4.0.5 on 2022-09-15 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0002_tournament_photo_alter_tournament_players_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tournament',
            options={'verbose_name': 'Турнир', 'verbose_name_plural': 'Турниры'},
        ),
        migrations.AlterField(
            model_name='tournament',
            name='date_end',
            field=models.DateField(verbose_name='Дата завершения'),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='date_start',
            field=models.DateField(verbose_name='Дата начала'),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='typo',
            field=models.CharField(choices=[('1vs1', 'Одиночный турнир'), ('2vs2', 'Командный турнир'), ('3vs3', 'Командный турнир'), ('4vs4', 'Командный турнир'), ('5vs5', 'Командный турнир')], default='1vs1', max_length=4, verbose_name='Тип турнира'),
        ),
    ]