# Generated by Django 4.0.5 on 2022-09-15 09:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_alter_teams_options_alter_user_team_invitations'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='news',
            options={'ordering': ['-date'], 'verbose_name': 'Новость', 'verbose_name_plural': 'Новости'},
        ),
    ]