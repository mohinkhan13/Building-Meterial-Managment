# Generated by Django 5.1 on 2024-09-02 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_picture',
            field=models.FileField(default=' ', upload_to='profile_picture/'),
        ),
    ]
