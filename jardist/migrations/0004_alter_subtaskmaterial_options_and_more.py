# Generated by Django 4.2 on 2024-06-26 03:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jardist', '0003_task_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subtaskmaterial',
            options={'verbose_name': 'Material Sub Pekerjaan', 'verbose_name_plural': 'Material Sub Pekerjaan'},
        ),
        migrations.AlterUniqueTogether(
            name='subtaskmaterial',
            unique_together=set(),
        ),
    ]
