# Generated by Django 4.2.6 on 2023-11-26 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_attos', '0014_reviews'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='perfil',
            field=models.TextField(blank=True, null=True),
        ),
    ]
