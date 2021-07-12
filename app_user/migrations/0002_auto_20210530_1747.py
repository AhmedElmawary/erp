# Generated by Django 3.2 on 2021-05-30 15:47

import _helpers.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='address',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='User Address'),
        ),
        migrations.AlterField(
            model_name='user',
            name='city',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='City name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=250, null=True, unique=True, verbose_name='User Email'),
        ),
        migrations.AlterField(
            model_name='user',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to=_helpers.models.user_img_upload_path, verbose_name='User Image'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=True, editable=False, verbose_name='Is staff'),
        ),
    ]
