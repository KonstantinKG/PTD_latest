# Generated by Django 4.0.5 on 2022-09-20 03:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0009_remove_tournament_teams_alter_tournament_players'),
        ('main', '0009_teams_tournaments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teams',
            name='tournaments',
        ),
        migrations.CreateModel(
            name='TeamParticapation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('particapants', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, verbose_name='Участники')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='teams', to='main.teams', verbose_name='Команда')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='particapants', to='tournaments.tournament', verbose_name='Турнир')),
            ],
            options={
                'verbose_name': 'Участие в турнире',
                'verbose_name_plural': 'Участие в турнирах',
                'unique_together': {('team', 'tournament')},
            },
        ),
    ]
