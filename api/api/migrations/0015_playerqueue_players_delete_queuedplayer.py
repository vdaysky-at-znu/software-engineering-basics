# Generated by Django 4.0 on 2022-10-30 15:06

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_playerqueue_captain_a_playerqueue_captain_b_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerqueue',
            name='players',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='QueuedPlayer',
        ),
    ]
