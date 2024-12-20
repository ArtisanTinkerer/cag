# Generated by Django 4.0.5 on 2022-07-17 12:54

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20220701_0858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='number_plate',
            field=models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message='Please only enter alphanumeric characters.', regex='^[A-Za-z0-9 ]*$')]),
        ),
        migrations.AlterField(
            model_name='donation',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name='donation',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='donations', to='core.customer'),
        ),
    ]
