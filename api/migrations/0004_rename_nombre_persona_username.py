# Generated by Django 5.1.1 on 2024-09-14 20:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_persona_delete_programmer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='persona',
            old_name='nombre',
            new_name='username',
        ),
    ]
