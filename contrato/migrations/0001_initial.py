# Generated by Django 4.1.7 on 2023-04-13 14:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('produto', '0002_produto_flinativo'),
        ('vendedor', '0001_initial'),
        ('cliente', '0003_rename_flativo_cliente_flinativo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contrato',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_contrato', models.DateField(blank=True, null=True)),
                ('data_instalacao', models.DateField(blank=True, null=True)),
                ('total_contrato', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('flcancelado', models.BooleanField(default=False)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cliente.cliente')),
                ('vendedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vendedor.vendedor')),
            ],
            options={
                'db_table': 'contrato',
            },
        ),
        migrations.CreateModel(
            name='EventoTipo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'evento_tipo',
            },
        ),
        migrations.CreateModel(
            name='ItemContrato',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.IntegerField(default=1)),
                ('valor_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('data_item', models.DateTimeField(auto_now_add=True)),
                ('flcancelado', models.BooleanField(default=False)),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contrato.contrato')),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='produto.produto')),
            ],
            options={
                'db_table': 'item_contrato',
            },
        ),
        migrations.CreateModel(
            name='ContratoEvento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evento_descricao', models.CharField(max_length=255)),
                ('evento_data', models.DateTimeField(auto_now_add=True)),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contrato.contrato')),
                ('evento_tipo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contrato.eventotipo')),
            ],
            options={
                'db_table': 'contrato_evento',
            },
        ),
    ]
