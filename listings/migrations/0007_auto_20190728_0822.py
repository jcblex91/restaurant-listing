# Generated by Django 2.2.3 on 2019-07-28 08:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0006_auto_20190728_0701'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Restaurant',
            new_name='ZomatoRestaurant',
        ),
    ]
