# Generated by Django 4.0 on 2022-10-30 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_game_winner_ingameteam_team_alter_round_game'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='mode',
            field=models.CharField(default='competitive', max_length=20),
            preserve_default=False,
        ),
    ]
