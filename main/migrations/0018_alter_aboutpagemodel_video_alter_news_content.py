# Generated by Django 4.0.5 on 2022-10-08 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_alter_news_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aboutpagemodel',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='about/videos/', verbose_name='Видео'),
        ),
        migrations.AlterField(
            model_name='news',
            name='content',
            field=models.TextField(help_text='Если вы копируете текст из сторонних источников и вставляете в это поле не забывается нажимать кнопку Т с крестиком снизу', verbose_name='Текст новости'),
        ),
    ]
