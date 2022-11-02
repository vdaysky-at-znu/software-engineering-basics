# Generated by Django 4.0 on 2022-10-31 19:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_match_game_meta'),
    ]

    operations = [
        migrations.AddField(
            model_name='mappickprocess',
            name='picker_a',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='api.player'),
        ),
        migrations.AddField(
            model_name='mappickprocess',
            name='picker_b',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='api.player'),
        ),
        migrations.AlterField(
            model_name='mappickprocess',
            name='turn',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.player'),
        ),
    ]