# Generated by Django 5.0.4 on 2024-09-20 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('t1', '0009_sender_rename_recipient_sender_recipient_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrier',
            name='EUEOPIID',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='проверка номера'),
        ),
        migrations.AlterField(
            model_name='recipient',
            name='EUEOPIID',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='проверка номера'),
        ),
        migrations.AlterField(
            model_name='sender',
            name='EUEOPIID',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='проверка номера'),
        ),
    ]