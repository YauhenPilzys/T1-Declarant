# Generated by Django 5.0.4 on 2024-05-21 14:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('t1', '0005_routes_remove_t1_xml_couofroucoditi1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='routes',
            name='t1_xml',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='t1.t1_xml', verbose_name='XML'),
            preserve_default=False,
        ),
    ]
