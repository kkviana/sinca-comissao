from django.shortcuts import render, redirect
from .models import Cliente, Produto, Contrato, ItemContrato, EventoTipo, ContratoEvento, Vendedor
import json
from django.contrib import messages
from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Q, Max, ExpressionWrapper, F, DateTimeField, Subquery, OuterRef

def novo_contrato(request):
    if request.method == 'POST':
        cliente_id = request.POST['cliente']
        total_contrato = request.POST['total_contrato']
        produtos = json.loads(request.POST['produtos'])
        data_contrato = request.POST['data_contrato']
        data_instalacao = request.POST['data_instalacao']
        vendedor_id = request.POST['vendedor']

        # create the Contrato instance
        contrato = Contrato(cliente_id=cliente_id, total_contrato=total_contrato, data_contrato=data_contrato, data_instalacao=data_instalacao, vendedor_id=vendedor_id)
        contrato.save()

        # create the ItemContrato instances
        for produto in produtos:
            produto_id = produto['id']
            quantidade = produto['quantidade']
            preco = produto['preco']

            item_contrato = ItemContrato(produto_id=produto_id, quantidade=quantidade, contrato=contrato, valor_unitario=preco)
            item_contrato.save()
        evento_tipo = EventoTipo.objects.get(id=7)  # ID do evento de adição de item
        evento = ContratoEvento.objects.create(contrato=contrato, evento_tipo=evento_tipo)
        evento.evento_descricao = 'Contrato Criado'
        evento.save()

        messages.success(request, 'Contrato salvo com sucesso.')
        return redirect('novo_contrato')
    clientes = Cliente.objects.all()
    produtos = Produto.objects.all()
    vendedores = Vendedor.objects.filter(flinativo=False)
    return render(request, 'novo_contrato.html', {'clientes': clientes, 'produtos': produtos, 'vendedores': vendedores})

def listar_contratos(request):
    contratos = Contrato.objects.all()
    return render(request, 'listar_contratos.html', {'contratos': contratos})

def editar_contrato(request, id_contrato):
    contrato = Contrato.objects.get(id=id_contrato)
    produtos = ItemContrato.objects.filter(contrato_id=id_contrato, flcancelado=False)
    eventos = ContratoEvento.objects.filter(contrato_id=id_contrato)
    return render(request, 'editar_contrato.html', {'contrato': contrato, 'produtos': produtos, 'eventos': eventos})

def adicionar_item_contrato(request, id_contrato):
    contrato = Contrato.objects.get(id=id_contrato)

    if request.method == 'POST':
        # Obter os dados do novo item do formulário
        produto_id = request.POST['produto']
        valor_unitario = request.POST['preco']
        quantidade = request.POST['quantidade']
        produto = Produto.objects.get(id=produto_id)
        item_contrato = ItemContrato(
            contrato=contrato,
            produto=produto,
            valor_unitario=float(valor_unitario),
            quantidade=int(quantidade)
        )
        item_contrato.save()

        # Atualizar o evento de adição de item ao contrato
        evento_tipo = EventoTipo.objects.get(id=3)  # ID do evento de adição de item
        evento = ContratoEvento.objects.create(contrato=contrato, evento_tipo=evento_tipo)
        evento.evento_descricao = f'Item adicionado: {item_contrato.produto.nome}'
        evento.save()
        atualiza_preco_contrato(id_contrato)

        messages.success(request, 'Item adicionado ao contrato com sucesso.')
        return redirect('editar_contrato', id_contrato=id_contrato) # Redirecionar para a página de edição do contrato
    produtos = Produto.objects.all()
    context = {'contrato': contrato, 'produtos': produtos}
    return render(request, 'adicionar_item_contrato.html', context)

def cancelar_item_contrato(request, id_item_contrato):
    item_contrato = ItemContrato.objects.get(id=id_item_contrato)

    if request.method == 'POST':
        motivo = 'teste remoção item - DESCRIÇÃO FIXA'

        # Criar um evento de cancelamento
        evento_tipo = EventoTipo.objects.get(nome='Remoção de itens')
        evento = ContratoEvento(
            evento_descricao = f'Item removido: {item_contrato.produto.nome}',
            contrato_id=item_contrato.contrato.id,
            evento_tipo_id=evento_tipo.id,
        )
        evento.save()
        # Atualizar o status do item de contrato para cancelado
        item_contrato.flcancelado = 1
        item_contrato.save()
        
        atualiza_preco_contrato(item_contrato.contrato.id)
        messages.success(request, 'Item de contrato cancelado com sucesso.')
        return redirect('editar_contrato', id_contrato=item_contrato.contrato.id)  # Redirecionar para a página de edição de contrato após o cancelamento do item

    context = {'item_contrato': item_contrato}
    return render(request, 'editar_item_contrato.html', context)

def cancelar_contrato(request, id_contrato):
    if request.method == 'POST':
        contrato = Contrato.objects.get(id=id_contrato)
        motivo = request.POST.get('motivo')

        # Criar um evento de cancelamento
        evento_tipo = EventoTipo.objects.get(nome='Cancelamento')
        evento = ContratoEvento(
            contrato_id=contrato.id,
            evento_tipo_id=evento_tipo.id,
            evento_descricao=motivo
        )
        evento.save()

        # Atualizar o status do contrato para cancelado
        contrato.flcancelado = 1
        contrato.save()

        messages.success(request, 'Contrato cancelado com sucesso.')
        return redirect('listar_contratos')  # Redirecionar para a página de sucesso após o cancelamento

    context = {'contrato': contrato}
    return render(request, 'listar_contratos.html', context)

def editar_item_contrato(request, id_item_contrato):
    item_contrato = ItemContrato.objects.get(id=id_item_contrato)
    contrato = item_contrato.contrato
    eventos_anteriores = ContratoEvento.objects.filter(contrato=contrato)
    if request.method == 'POST':
        novo_valor = request.POST['valor_unitario']
        nova_quantidade = request.POST['quantidade']
        if novo_valor:
            novo_valor = float(novo_valor)
            if novo_valor != item_contrato.valor_unitario:
                evento_tipo = EventoTipo.objects.get(nome='Ajuste de valor')
                descricao = f'Valor do produto: {item_contrato.id} - {item_contrato.produto.nome}, alterado de {item_contrato.valor_unitario} para {novo_valor}.'
                evento = ContratoEvento(contrato=contrato, evento_descricao=descricao, evento_tipo=evento_tipo)
                evento.save()
                item_contrato.valor_unitario = novo_valor
        if nova_quantidade:
            nova_quantidade = int(nova_quantidade)
            if nova_quantidade != item_contrato.quantidade:
                evento_tipo = EventoTipo.objects.get(nome='Ajuste de quantidade')
                descricao = f'Quantidade do produto: {item_contrato.id} - {item_contrato.produto.nome}, alterada de {item_contrato.quantidade} para {nova_quantidade}.'
                evento = ContratoEvento(contrato=contrato, evento_descricao=descricao, evento_tipo=evento_tipo)
                evento.save()
                item_contrato.quantidade = nova_quantidade
        item_contrato.save()
        atualiza_preco_contrato(item_contrato.contrato.id)
        return redirect('editar_contrato', id_contrato=contrato.id)
    return render(request, 'editar_item_contrato.html', {'item_contrato': item_contrato, 'eventos_anteriores': eventos_anteriores})

def atualiza_preco_contrato(id_contrato):
    contrato = Contrato.objects.get(id=id_contrato)
    itens_contrato = ItemContrato.objects.filter(contrato=contrato, flcancelado=False)
    total_contrato = 0

    # Calcular a soma dos valores dos itens de contrato
    for item in itens_contrato:
        total_contrato += item.valor_unitario * item.quantidade
        print(total_contrato)
    # Atualizar o valor do contrato com o total calculado
    contrato.total_contrato = total_contrato
    contrato.save()

    return total_contrato

def atualizar_contratos(request):
    # Obtém a data atual
    data_atual = date.today()

    # Subtrai um ano da data atual para obter a data de referência
    data_referencia = date(data_atual.year - 1, data_atual.month, data_atual.day)

    # Busca os contratos que foram feitos há mais de 1 ano e não têm reajustes
    contratos_sem_reajuste = Contrato.objects.filter(
        Q(data_contrato__lt=data_referencia) & Q(flcancelado=False)
    ).exclude(
        contratoevento__evento_tipo_id=8
    )
    # Subconsulta para obter o último evento do tipo 8 de cada contrato
    subquery = ContratoEvento.objects.filter(
        contrato_id=OuterRef('pk'), evento_tipo_id=8
    ).order_by('-evento_data').values('evento_data')[:1]

    contratos_reajuste_antigo = Contrato.objects.filter(
        contratoevento__evento_tipo_id=8,
        contratoevento__evento_data__lt=data_referencia,
        contratoevento__evento_data=Subquery(subquery)
    )
    contratos_para_ajustar = contratos_sem_reajuste | contratos_reajuste_antigo
    contratos_para_ajustar = contratos_para_ajustar.distinct()

    if request.method == 'POST':
        # Captura a porcentagem de reajuste informada pelo usuário
        porcentagem = float(request.POST.get('porcentagem'))
        porcentagem_decimal = Decimal(str(porcentagem / 100))
        contratos_marcados = request.POST.getlist('contratos_marcados')
        print(contratos_marcados)

        # Atualiza o preço dos itens de contrato com base na porcentagem informada
        for contrato_id in contratos_marcados:
            contrato = Contrato.objects.get(id=contrato_id)
            valor_contrato = contrato.total_contrato
            total_itens = contrato.itemcontrato_set.all().count()

            for item in contrato.itemcontrato_set.all():
                acrescimo_por_item = (item.valor_unitario * porcentagem_decimal)
                novo_valor_item = item.valor_unitario + acrescimo_por_item
                quantidade = item.quantidade
                novo_valor_total = novo_valor_item * quantidade
                item.valor_unitario = novo_valor_item
                item.valor_total = novo_valor_total
                item.save()

            evento_tipo = EventoTipo.objects.get(nome='Reajuste anual')
            descricao = f'Ajustado o valor do contrato: {contrato.id} em {porcentagem}%.'
            evento = ContratoEvento(
                contrato_id=contrato.id,
                evento_tipo_id=evento_tipo.id,
                evento_descricao=descricao
            )
            evento.save()

            # Chama a função atualiza_preco_contrato apenas uma vez para cada contrato
            atualiza_preco_contrato(contrato.id)

    contratos = Contrato.objects.filter()
    context = {'contratos_para_ajustar': contratos_para_ajustar, 'contratos': contratos}
    return render(request, 'atualizar_contratos.html', context)

