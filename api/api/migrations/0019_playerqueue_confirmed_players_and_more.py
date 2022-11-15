# Generated by Django 4.0 on 2022-10-30 19:03

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_playerqueue_confirmed_playerqueue_locked_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerqueue',
            name='confirmed_players',
            field=models.ManyToManyField(related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='playerqueue',
            name='players',
            field=models.ManyToManyField(related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='PlayerConfirmation',
        ),
    ]
