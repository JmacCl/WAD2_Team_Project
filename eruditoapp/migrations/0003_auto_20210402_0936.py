# Generated by Django 2.2.17 on 2021-04-02 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eruditoapp', '0002_auto_20210331_1010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='picture',
            field=models.ImageField(blank=True, default='default.jpg', upload_to='profile_images'),
        ),
    ]
