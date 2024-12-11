# Generated by Django 5.1.1 on 2024-11-23 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_persona_is_active_persona_is_staff_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='persona',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='persona',
            name='is_staff',
        ),
        migrations.RemoveField(
            model_name='persona',
            name='is_superuser',
        ),
        migrations.RemoveField(
            model_name='persona',
            name='last_login',
        ),
        migrations.AlterField(
            model_name='persona',
            name='correo',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='persona',
            name='password',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='persona',
            name='username',
            field=models.CharField(max_length=100),
        ),
    ]
