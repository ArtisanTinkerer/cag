# Generated by Django 4.0.5 on 2022-07-17 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_remove_donation_car_donation_number_plate_delete_car'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
    ]
