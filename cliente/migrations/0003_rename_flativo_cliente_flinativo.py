# Generated by Django 4.1.7 on 2023-04-11 22:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0002_cliente_flativo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cliente',
            old_name='flativo',
            new_name='flinativo',
        ),
    ]
