# Generated by Django 4.2.5 on 2023-11-03 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_attos', '0007_remove_fotos_last_updated_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='instagramprofile',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
