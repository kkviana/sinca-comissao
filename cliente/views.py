from django.shortcuts import render, redirect, get_object_or_404
from meuapp.utils import login_required_all
from .models import Cliente, Timestamp
from produto.models import Produto
from contrato.models import Contrato
from vendedor.models import Vendedor
from contrato.models import ItemContrato
from contrato.models import ContratoEvento
from contrato.models import EventoTipo
from django.contrib.auth.models import User
from .forms import ClienteForm
import csv
from django.http import HttpResponse
import datetime
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import call_command
from django.db.models import Sum, F, FloatField, DecimalField, Q
import mysql.connector
import time





@login_required_all
def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    
    return render(request, 'cadastrar_cliente.html', {'form': form})

@login_required_all
def lista_clientes(request):
    clientes = Cliente.objects.filter(flinativo=False)
    return render(request, 'lista_clientes.html', {'clientes': clientes})

@login_required_all
def editar_cliente(request, id_cliente):
    cliente = get_object_or_404(Cliente, id=id_cliente)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    context = {'form': form}
    return render(request, 'editar_cliente.html', context)  

@login_required_all
def inativar_cliente(request, id_cliente):
    cliente = Cliente.objects.get(id=id_cliente)
    cliente.flinativo = True
    cliente.save()
    return redirect('lista_clientes') # Redirecionar para a página do cliente
    
@login_required_all
def load_data_from_csv(filename):
    #Limpar os dados
    call_command('flush', '--no-input')

    # Cria ou atualiza um superuser
    user = User.objects.create_superuser('kaue', '', 'kaue')
    user.save()

    timestamp = Timestamp(id=1, timestamp=0)
    timestamp.save()

    # Cria tipo de eventos
    evento1 = EventoTipo(nome='Ajuste de valor')
    evento1.save()
    evento2 = EventoTipo(nome='Remoção de itens')
    evento2.save()
    evento3 = EventoTipo(nome='Adição de itens')
    evento3.save()
    evento4 = EventoTipo(nome='Cancelamento')
    evento4.save()
    evento5 = EventoTipo(nome='Ajuste de quantidade')
    evento5.save()
    evento6 = EventoTipo(nome='Hard Shop Informática')
    evento6.save()
    evento7 = EventoTipo(nome='Criação Contrato')
    evento7.save()
    evento8 = EventoTipo(nome='Reajuste anual')
    evento8.save()

    #importar Vendedor
    vendedor1 = Vendedor(nome='Hard Shop Informática')
    vendedor1.save()
    vendedor2 = Vendedor(nome='Fabiano')
    vendedor2.save()
    vendedor3 = Vendedor(nome='Paty/Tais')
    vendedor3.save()
    #importar Produtos
    produto1 = Produto(nome='SINCA Premium', descricao='SINCA Premium', preco=160)
    produto1.save()
    produto2 = Produto(nome='SINCA Hair', descricao='SINCA Hair', preco=160)
    produto2.save()
    produto3 = Produto(nome='SINCA PAF-NFCe', descricao='SINCA PAF-NFCe', preco=160)
    produto3.save()
    produto4 = Produto(nome='SINCA PAF-ECF', descricao='SINCA PAF-ECF', preco=160)
    produto4.save()
    produto5 = Produto(nome='SINCA NFe', descricao='SINCA NFe', preco=160)
    produto5.save()
    produto6 = Produto(nome='SINCA CTe', descricao='SINCA CTe', preco=160)
    produto6.save()
    produto7 = Produto(nome='Micros', descricao='Mircros', preco=40)
    produto7.save()
    produto8 = Produto(nome='DAV', descricao='DAV', preco=160)
    produto8.save()

    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Pula a primeira linha do arquivo CSV (que pode ser um cabeçalho)
        for row in reader:

            #tabela Contrato
            if row[4]:
                cancelado = True
            else:
                cancelado = False

            data_contrato = datetime.datetime.strptime(row[2], '%d/%m/%Y').strftime('%Y-%m-%d')
            data_instalacao = datetime.datetime.strptime(row[3], '%d/%m/%Y').strftime('%Y-%m-%d')

            valor = row[1].strip().replace(',', '.')  # Remove espaços e substitui vírgulas por pontos
            valor_decimal = Decimal(valor)
            if row[17] == 'Fabiano':
                vendedor = vendedor2.id
            if row[17] == 'Paty/Tais':
                vendedor = vendedor3.id
            else:
                vendedor = vendedor1.id

            contrato = Contrato(data_contrato=data_contrato, total_contrato=valor_decimal, cliente_id=row[16], data_instalacao=data_instalacao, flcancelado=cancelado, vendedor_id=vendedor)
            contrato.save()

            # Criar registros na tabela ItemContrato para os produtos relacionados ao contrato atual
            produtos_adicionados = set()

            # Criar registros na tabela ItemContrato para os produtos relacionados ao contrato atual
            for i in range(7, 14):
                if row[7] != '' and (row[10] != '' or row[9] != ''):
                    if row[10] != '':
                        produto1 = produto4
                        produto2 = produto8
                    else:
                        produto1 = produto3
                        produto2 = produto8

                    produto3 = produto7
                    quantidade = row[13]

                    if produto1 not in produtos_adicionados:
                        item_contrato = ItemContrato(contrato=contrato, produto=produto1, valor_unitario=produto1.preco, quantidade=1)
                        item_contrato.save()
                        produtos_adicionados.add(produto1)

                    if produto2 not in produtos_adicionados:
                        item_contrato = ItemContrato(contrato=contrato, produto=produto2, valor_unitario=produto2.preco, quantidade=1)
                        item_contrato.save()
                        produtos_adicionados.add(produto2)

                    if produto3 not in produtos_adicionados:
                        item_contrato = ItemContrato(contrato=contrato, produto=produto3, valor_unitario=produto3.preco, quantidade=quantidade)
                        item_contrato.save()
                        produtos_adicionados.add(produto3)
                else:
                    if row[i] != '':
                        # Associar o produto correspondente ao contrato atual
                        if i == 7:
                            produto = produto1
                            quantidade = 1
                        elif i == 8:
                            produto = produto2
                            quantidade = 1
                        elif i == 9:
                            produto = produto3
                            quantidade = 1
                        elif i == 10:
                            produto = produto4
                            quantidade = 1
                        elif i == 11:
                            produto = produto5
                            quantidade = 1
                        elif i == 12:
                            produto = produto6
                            quantidade = 1
                        else:
                            produto = produto7
                            quantidade = row[13]

                        if produto not in produtos_adicionados:
                            item_contrato = ItemContrato(contrato=contrato, produto=produto, valor_unitario=produto.preco, quantidade=quantidade)
                            item_contrato.save()
                            produtos_adicionados.add(produto)

            if row[4]:
                data = datetime.datetime.strptime(row[4], '%d/%m/%Y')
                evento = ContratoEvento(contrato=contrato, evento_descricao='Cancelados da importação', evento_data=data, evento_tipo_id=4)
                evento.save()

@login_required_all
def desconto_segundo_item():
    produtos_codigos = [1, 2, 3, 4, 5, 6, 8]
    contratos = Contrato.objects.filter(itemcontrato__produto__id__in=produtos_codigos).distinct()
    for contrato in contratos:
        produtos_contrato = ItemContrato.objects.filter(contrato=contrato, produto__id__in=produtos_codigos)
        if len(produtos_contrato) == 2:
            # Ordena os produtos por ID para garantir que o desconto sempre seja aplicado ao mesmo produto
            produtos_contrato = produtos_contrato.order_by('id')

            # Calcule o desconto de 50% no valor_unitario de todos os itens, exceto o primeiro
            for i, item_contrato in enumerate(produtos_contrato):
                if i > 0:
                    item_contrato.valor_unitario *= Decimal('0.5')
                item_contrato.save()

@login_required_all
def atualizar_precos():
    # Filtra contratos onde o total_contrato é diferente da soma dos itens
    contratos = Contrato.objects.annotate(
        soma_itens=Sum(F('itemcontrato__valor_unitario') * F('itemcontrato__quantidade'), output_field=DecimalField())
    ).filter(~Q(total_contrato=F('soma_itens')))

    # Atualiza o preço dos itens com o desconto ou acréscimo proporcional à diferença entre o total_contrato e a soma dos itens
    for contrato in contratos:
        soma_itens = contrato.soma_itens
        porcentual = contrato.total_contrato / soma_itens

        itens_contrato = ItemContrato.objects.filter(contrato=contrato)
        for item_contrato in itens_contrato:
            novo_valor_unitario = item_contrato.valor_unitario * porcentual
            item_contrato.valor_unitario = novo_valor_unitario
            item_contrato.save()

@login_required_all
def importar(request):
    filename = request.GET.get('filename', None)
    if filename:
        load_data_from_csv(filename)
        desconto_segundo_item()
        atualizar_precos()
        return HttpResponse('Dados importados com sucesso.')
    else:
        return HttpResponse('O nome do arquivo não foi informado.')

@login_required_all
def sincronizar_clientes(request):
    local_cnx = mysql.connector.connect(user='', password='',
                                         host='', database='')
    local_cursor = local_cnx.cursor()
    local_cursor.execute("SELECT timestamp FROM timestamp WHERE id=1")
    row = local_cursor.fetchone()
    timestamp = row[0] if row else 0

    # Conectar ao banco de dados remoto MariaDB e executar consulta com filtro de timestamp
    remote_cnx = mysql.connector.connect(user='sinca_comissao', password='Wd0712wd!',
                                          host='bd.hardshop.com.br', database='sinca_hard')
    remote_cursor = remote_cnx.cursor()
    query = f"SELECT cdcliente, nmcliente, cdtipocli, timestamp FROM cliente WHERE timestamp > {timestamp}"
    remote_cursor.execute(query)

    # Iterar sobre os resultados e criar ou atualizar as instâncias de Cliente
    for (cdcliente, nmcliente, cdtipocli, remote_timestamp) in remote_cursor:
        cliente, created = Cliente.objects.update_or_create(
            id=cdcliente,
            defaults={'nome': nmcliente, 'flinativo': cdtipocli != 5}
        )
        # atualizar o valor do timestamp local com o maior valor do timestamp remoto
        if remote_timestamp > timestamp:
            timestamp = remote_timestamp

    # Atualizar o valor do timestamp na tabela local
    local_cursor.execute(f"REPLACE INTO timestamp (id, timestamp) VALUES (1, {timestamp})")
    local_cnx.commit()

    # Fechar as conexões com os bancos de dados
    remote_cursor.close()
    remote_cnx.close()
    local_cursor.close()
    local_cnx.close()