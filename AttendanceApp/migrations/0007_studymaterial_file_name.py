# Generated by Django 4.2.7 on 2024-03-24 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AttendanceApp', '0006_studymaterial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studymaterial',
            name='file_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
