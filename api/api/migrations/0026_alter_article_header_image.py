# Generated by Django 4.0 on 2022-11-02 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_article_header_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='header_image',
            field=models.CharField(max_length=1024, null=True),
        ),
    ]
