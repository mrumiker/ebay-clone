# Generated by Django 3.2.5 on 2021-09-06 03:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0014_alter_album_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='selling', to=settings.AUTH_USER_MODEL),
        ),
    ]
