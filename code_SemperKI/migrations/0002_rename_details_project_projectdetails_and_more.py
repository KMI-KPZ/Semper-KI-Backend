# Generated by Django 4.2.7 on 2023-12-22 12:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('code_SemperKI', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='details',
            new_name='projectDetails',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='status',
            new_name='projectStatus',
        ),
    ]
