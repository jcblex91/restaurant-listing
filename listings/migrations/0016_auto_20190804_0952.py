# Generated by Django 2.2.3 on 2019-08-04 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0015_googlerestaurants_photo_ref'),
    ]

    operations = [
        migrations.RenameField(
            model_name='googlerestaurants',
            old_name='photo_ref',
            new_name='photo_url',
        ),
    ]