# Generated by Django 4.0 on 2022-09-25 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_alter_mappickprocess_turn'),
    ]

    operations = [
        migrations.AddField(
            model_name='mappick',
            name='map_codename',
            field=models.CharField(default='mirage', max_length=100),
            preserve_default=False,
        ),
    ]
