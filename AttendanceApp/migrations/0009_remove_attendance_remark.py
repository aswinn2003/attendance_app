# Generated by Django 4.2.7 on 2024-03-28 16:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AttendanceApp', '0008_attendance_remark'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='remark',
        ),
    ]
