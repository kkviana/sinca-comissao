# Generated by Django 4.1.7 on 2023-04-28 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    operations = [
        migrations.CreateModel(
            name='Timestamp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Timestamp', models.IntegerField()),
            ],
            options={
                'db_table': 'timestamp',
            },
        ),
    ]
