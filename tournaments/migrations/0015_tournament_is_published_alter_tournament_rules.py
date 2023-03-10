# Generated by Django 4.0.5 on 2022-10-01 10:49

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0014_alter_status_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='is_published',
            field=models.BooleanField(default=True, verbose_name='Опубликовать'),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='rules',
            field=tinymce.models.HTMLField(verbose_name='Правила'),
        ),
    ]
