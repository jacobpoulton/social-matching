# Generated by Django 4.1.7 on 2023-04-01 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdetails',
            name='agreeableness',
            field=models.DecimalField(decimal_places=3, default=0.5, max_digits=3),
        ),
        migrations.AddField(
            model_name='userdetails',
            name='extroversion',
            field=models.DecimalField(decimal_places=3, default=0.5, max_digits=3),
        ),
        migrations.AddField(
            model_name='userdetails',
            name='neuroticism',
            field=models.DecimalField(decimal_places=3, default=0.5, max_digits=3),
        ),
    ]
