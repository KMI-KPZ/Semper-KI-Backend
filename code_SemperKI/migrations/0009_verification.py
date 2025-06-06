# Generated by Django 4.2.7 on 2025-01-30 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('code_SemperKI', '0008_delete_event'),
    ]

    operations = [
        migrations.CreateModel(
            name='Verification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organizationID', models.CharField(max_length=512)),
                ('printerID', models.CharField(max_length=512)),
                ('materialID', models.CharField(max_length=512)),
                ('status', models.IntegerField()),
                ('details', models.JSONField()),
                ('createdWhen', models.DateTimeField(auto_now_add=True)),
                ('updatedWhen', models.DateTimeField(auto_now=True)),
                ('accessedWhen', models.DateTimeField(auto_now=True)),
            ],
            options={
                'indexes': [models.Index(fields=['organizationID'], name='organizationID_idx')],
            },
        ),
    ]
