# Generated by Django 4.1.7 on 2023-04-17 16:41

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_userdetails_agreeableness_userdetails_extroversion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='users',
            field=models.ManyToManyField(null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]