# Generated by Django 2.2.3 on 2019-08-04 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0014_auto_20190731_1842'),
    ]

    operations = [
        migrations.AddField(
            model_name='googlerestaurants',
            name='photo_ref',
            field=models.TextField(default=None),
        ),
    ]
