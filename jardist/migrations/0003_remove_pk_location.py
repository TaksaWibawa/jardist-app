# Generated by Django 4.2 on 2024-06-27 21:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jardist', '0002_initial-data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pk',
            name='location',
        ),
    ]
