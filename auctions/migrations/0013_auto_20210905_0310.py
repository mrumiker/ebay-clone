# Generated by Django 3.2.5 on 2021-09-05 03:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_alter_album_genres'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(max_length=1024),
        ),
        migrations.AlterField(
            model_name='genre',
            name='description',
            field=models.TextField(max_length=1024),
        ),
    ]
