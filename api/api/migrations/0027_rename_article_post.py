# Generated by Django 4.0 on 2022-11-02 16:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_alter_article_header_image'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Article',
            new_name='Post',
        ),
    ]
