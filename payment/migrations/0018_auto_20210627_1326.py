# Generated by Django 3.2 on 2021-06-27 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0017_alter_paymenttransactiontype_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymenttransactiontype',
            name='for_client',
            field=models.BooleanField(default=False, verbose_name='For client'),
        ),
        migrations.AddField(
            model_name='paymenttransactiontype',
            name='for_supplier',
            field=models.BooleanField(default=False, verbose_name='For supplier'),
        ),
    ]
