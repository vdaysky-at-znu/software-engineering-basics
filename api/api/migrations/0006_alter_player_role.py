# Generated by Django 4.0 on 2022-09-10 10:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_player_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='api.role'),
        ),
    ]
