# Generated by Django 5.0.4 on 2024-05-15 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('t1', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='structure',
            name='NAME_EN',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='t1_xml',
            name='AccCodREF6',
            field=models.CharField(max_length=255, verbose_name='код гарантийного сертификата'),
        ),
    ]