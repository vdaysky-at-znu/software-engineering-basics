# Generated by Django 4.0 on 2022-10-31 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_playerqueue_confirmed_players_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='game_meta',
            field=models.JSONField(default={'mode': 'competitive'}),
            preserve_default=False,
        ),
    ]
