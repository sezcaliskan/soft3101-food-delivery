# Generated by Django 3.1.2 on 2021-01-09 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_auto_20210109_1903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='city',
            field=models.CharField(choices=[('Istanbul', 'Istanbul'), ('Ankara', 'Ankara'), ('Izmir', 'Izmir'), ('Antalya', 'Antalya')], max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='city',
            field=models.CharField(choices=[('Istanbul', 'Istanbul'), ('Ankara', 'Ankara'), ('Izmir', 'Izmir'), ('Antalya', 'Antalya')], max_length=200, null=True),
        ),
        migrations.DeleteModel(
            name='City',
        ),
    ]
