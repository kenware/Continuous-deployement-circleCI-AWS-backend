# Generated by Django 2.2.3 on 2019-07-28 20:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('favorite_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favoritethings',
            name='modified_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
