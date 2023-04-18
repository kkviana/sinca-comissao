# Generated by Django 4.1.7 on 2023-04-12 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Vendedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('flinativo', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'vendedor',
            },
        ),
    ]