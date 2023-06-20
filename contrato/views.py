from django.shortcuts import render, redirect
from .models import Cliente, Produto, Contrato, ItemContrato, EventoTipo, ContratoEvento, Vendedor
import json
from django.contrib import messages
from datetime import date
from decimal import Decimal
from django.db.models import Q, Subquery, OuterRef
from django.db.models.functions import Upper
from django.core.paginator import Paginator
from cliente.views import sincronizar_clientes
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from meuapp.utils import login_required_all
from django.db.models import Sum
from datetime import datetime
import calendar

@login_required_all
def novo_contrato(request):
    sincronizar_clientes(request)
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        print(cliente_id)
        total_contrato = request.POST.get('total_contrato')
        produtos = json.loads(request.POST.get('produtos', '[]'))
        data_contrato = request.POST.get('data_contrato')
        data_instalacao = request.POST.get('data_instalacao')
        vendedor_id = request.POST.get('vendedor')

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
        evento_tipo = EventoTipo.objects.get(id=7)
        evento = ContratoEvento.objects.create(contrato=contrato, evento_tipo=evento_tipo)
        evento.evento_descricao = 'Contrato Criado'
        evento.save()

        messages.success(request, 'Contrato salvo com sucesso.')
        return redirect('novo_contrato')
    clientes = Cliente.objects.filter(flinativo=False).order_by('nome')
    produtos = Produto.objects.all()
    vendedores = Vendedor.objects.filter(flinativo=False)
    return render(request, 'novo_contrato.html', {'clientes': clientes, 'produtos': produtos, 'vendedores': vendedores})

@login_required_all
def listar_contratos(request):
    contratos = Contrato.objects.filter(flcancelado=False)
    vendedores = Vendedor.objects.filter(flinativo=False)

    # Verifica se os parâmetros de filtro foram passados na requisição GET
    filtro_data_inicio = request.GET.get('data_inicio')
    filtro_data_fim = request.GET.get('data_fim')
    filtro_data_inicio_alteracao = request.GET.get('data_inicio_alteracao')
    filtro_data_fim_alteracao = request.GET.get('data_fim_alteracao')
    filtro_nome_cliente = request.GET.get('cliente')
    filtro_nome_vendedor = request.GET.get('vendedor')
    filtro_codigo_cliente = request.GET.get('codigo_cliente')

    if filtro_data_inicio:
        contratos = contratos.filter(data_instalacao__gte=filtro_data_inicio)

    if filtro_data_fim:
        contratos = contratos.filter(data_instalacao__lte=filtro_data_fim)

    if filtro_data_inicio_alteracao:
        contratos = contratos.filter(contratoevento__evento_data__gte=filtro_data_inicio_alteracao).distinct()

    if filtro_data_fim_alteracao:
        contratos = contratos.filter(contratoevento__evento_data__lte=filtro_data_fim_alteracao).distinct()

    if filtro_nome_vendedor:
        contratos = contratos.filter(vendedor__id=filtro_nome_vendedor)

    if filtro_codigo_cliente:
        contratos = contratos.filter(cliente__id=filtro_codigo_cliente)

    if filtro_nome_cliente:
        contratos = contratos.annotate(nome_cliente_upper=Upper('cliente__nome')).filter(nome_cliente_upper__icontains=filtro_nome_cliente.upper())

    contratos_filtrados = contratos.all()

    total_contratos = contratos_filtrados.aggregate(total=Sum('total_contrato'))['total'] or 0
    page = request.GET.get('pagina', 1)
    paginator = Paginator(contratos_filtrados, 40)  # Exibe 10 contratos por página
    contratos_pagina = paginator.get_page(page)

    return render(request, 'listar_contratos.html', {'contratos': contratos_pagina, 'vendedores': vendedores, 'total_contratos': total_contratos})

@login_required_all
def relatorio_contratos(request):
    contratos = request.GET.getlist('contratos')

    if not contratos:
        messages.warning(request, 'Selecione ao menos um contrato para visualizar.')
        return redirect('index')

    # Cria uma lista de strings, onde cada string representa um código de contrato
    contratos_lista = [c.strip() for c in contratos[0].split(',') if c.strip()]

    # Cria a lista de contratos a partir da lista de strings
    contratos = [int(c) for c in contratos_lista if c.isdigit()]

    if not contratos:
        return HttpResponse('Nenhum contrato selecionado para o relatório.')
    template_path = 'relatorio_contratos.html'
    context = {'contratos': Contrato.objects.filter(pk__in=contratos)}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_contratos.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pdf = pisa.CreatePDF(BytesIO(html.encode('UTF-8')), response)

    if not pdf.err:
        return response

    return HttpResponse('Erro ao gerar PDF: {}'.format(pdf.err))

@login_required_all
def editar_contrato(request, id_contrato):
    contrato = Contrato.objects.get(id=id_contrato)
    produtos = ItemContrato.objects.filter(contrato_id=id_contrato, flcancelado=False)
    eventos = ContratoEvento.objects.filter(contrato_id=id_contrato)
    return render(request, 'editar_contrato.html', {'contrato': contrato, 'produtos': produtos, 'eventos': eventos})

@login_required_all
def adicionar_item_contrato(request, id_contrato):
    contrato = Contrato.objects.get(id=id_contrato)

    if request.method == 'POST':
        produtos = json.loads(request.POST['produtos'])
        for produto in produtos:
            # Obter os dados do novo item do formulário
            produto_id = produto['id']
            valor_unitario = Decimal(produto['preco'])
            quantidade = int(produto['quantidade'])
            produto_obj = Produto.objects.get(id=produto_id)
            item_contrato = ItemContrato(
                contrato=contrato,
                produto=produto_obj,
                valor_unitario=valor_unitario,
                quantidade=quantidade
            )
            item_contrato.save()

            # Calcular o valor alterado do contrato
            valor_alterado = valor_unitario * quantidade

            # Atualizar o evento de adição de item ao contrato
            evento_tipo = EventoTipo.objects.get(id=3)  # ID do evento de adição de item
            evento = ContratoEvento.objects.create(contrato=contrato, evento_tipo=evento_tipo)
            evento.evento_descricao = f'Item adicionado: {item_contrato.produto.nome}'
            evento.valor_alterado = valor_alterado
            evento.save()

            atualiza_preco_contrato(contrato.id)

        messages.success(request, 'Itens adicionados ao contrato com sucesso.')
        return redirect('editar_contrato', id_contrato=id_contrato)  # Redirecionar para a página de edição do contrato

    produtos = Produto.objects.all()
    context = {'contrato': contrato, 'produtos': produtos}
    return render(request, 'adicionar_item_contrato.html', context)

@login_required_all
def cancelar_item_contrato(request, id_item_contrato):
    item_contrato = ItemContrato.objects.get(id=id_item_contrato)

    if request.method == 'POST':
        motivo = 'teste remoção item - DESCRIÇÃO FIXA'

        # Criar um evento de cancelamento
        evento_tipo = EventoTipo.objects.get(nome='Remoção de itens')
        valor_alterado = item_contrato.valor_unitario * item_contrato.quantidade * -1
        evento = ContratoEvento(
            evento_descricao=f'Item removido: {item_contrato.produto.nome}',
            contrato_id=item_contrato.contrato.id,
            evento_tipo_id=evento_tipo.id,
            valor_alterado=valor_alterado
        )
        evento.save()

        # Atualizar o status do item de contrato para cancelado
        item_contrato.flcancelado = True
        item_contrato.save()

        atualiza_preco_contrato(item_contrato.contrato.id)
        messages.success(request, 'Item de contrato cancelado com sucesso.')
        return redirect('editar_contrato', id_contrato=item_contrato.contrato.id)  # Redirecionar para a página de edição de contrato após o cancelamento do item

    context = {'item_contrato': item_contrato}
    return render(request, 'editar_item_contrato.html', context)

@login_required_all
def cancelar_contrato(request, id_contrato):
    if request.method == 'POST':
        contrato = Contrato.objects.get(id=id_contrato)
        motivo = request.POST.get('motivo')
        data_cancelamento_str = request.POST.get('data_cancelamento')
        data_cancelamento = datetime.strptime(data_cancelamento_str, '%Y-%m-%d').date()
        data_cancelamento = datetime.combine(data_cancelamento, datetime.min.time())  # Combine with minimum time

        # Criar um evento de cancelamento
        evento_tipo = EventoTipo.objects.get(nome='Cancelamento')
        evento = ContratoEvento(
            contrato_id=contrato.id,
            evento_tipo_id=evento_tipo.id,
            evento_descricao=motivo,
            valor_alterado=0,
        )
        evento.evento_data = data_cancelamento  # Set the custom date here
        evento.save()

        # Atualizar o status do contrato para cancelado
        contrato.flcancelado = 1
        contrato.save()

        messages.success(request, 'Contrato cancelado com sucesso.')
        return redirect('listar_contratos')  # Redirecionar para a página de sucesso após o cancelamento

    context = {'contrato': contrato}
    return render(request, 'listar_contratos.html', context)

@login_required_all
def editar_item_contrato(request, id_item_contrato):
    item_contrato = ItemContrato.objects.get(id=id_item_contrato)
    contrato = item_contrato.contrato
    eventos_anteriores = ContratoEvento.objects.filter(contrato=contrato)
    if request.method == 'POST':
        novo_valor = request.POST['valor_unitario']
        nova_quantidade = request.POST['quantidade']
        if novo_valor:
            novo_valor = Decimal(novo_valor)
            if novo_valor != item_contrato.valor_unitario:
                evento_tipo = EventoTipo.objects.get(nome='Ajuste de valor')
                descricao = f'Valor do produto: {item_contrato.id} - {item_contrato.produto.nome}, alterado de {item_contrato.valor_unitario} para {novo_valor}.'
                valor_alterado = (novo_valor - item_contrato.valor_unitario) * item_contrato.quantidade
                evento = ContratoEvento(contrato=contrato, evento_descricao=descricao, evento_tipo=evento_tipo)
                evento.valor_alterado = valor_alterado
                evento.save()
                item_contrato.valor_unitario = novo_valor
        if nova_quantidade:
            nova_quantidade = int(nova_quantidade)
            if nova_quantidade != item_contrato.quantidade:
                evento_tipo = EventoTipo.objects.get(nome='Ajuste de quantidade')
                descricao = f'Quantidade do produto: {item_contrato.id} - {item_contrato.produto.nome}, alterada de {item_contrato.quantidade} para {nova_quantidade}.'
                valor_alterado = (item_contrato.valor_unitario - novo_valor) * Decimal(nova_quantidade - item_contrato.quantidade)
                evento = ContratoEvento(contrato=contrato, evento_descricao=descricao, evento_tipo=evento_tipo)
                evento.valor_alterado = valor_alterado
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
    # Atualizar o valor do contrato com o total calculado
    contrato.total_contrato = total_contrato
    contrato.save()

    return total_contrato

@login_required_all
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

        # Atualiza o preço dos itens de contrato com base na porcentagem informada
        for contrato_id in contratos_marcados:
            contrato = Contrato.objects.get(id=contrato_id)
            valor_contrato = contrato.total_contrato
            total_itens = contrato.itemcontrato_set.all().count()
            valor_alterado = valor_contrato * porcentagem_decimal

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
                evento_descricao=descricao,
                valor_alterado=valor_alterado
            )
            evento.save()

            # Chama a função atualiza_preco_contrato apenas uma vez para cada contrato
            atualiza_preco_contrato(contrato.id)

    contratos = Contrato.objects.filter(flcancelado=False)
    context = {'contratos_para_ajustar': contratos_para_ajustar, 'contratos': contratos}
    return render(request, 'atualizar_contratos.html', context)

@login_required_all
def detalhes_aumento_contratos(request):
    if request.method == 'POST':
        # Obtenha o ano e o mês selecionados pelo usuário
        ano_selecionado = int(request.POST.get('ano'))
        mes_selecionado = int(request.POST.get('mes'))

        # Crie um objeto datetime com o ano e mês selecionados
        data_selecionada = datetime(ano_selecionado, mes_selecionado, 1)

        # Realize a consulta para obter o valor aumentado em reajustes e alterações de contratos
        eventos_aumento = ContratoEvento.objects.filter(
            evento_data__year=ano_selecionado,
            evento_data__month=mes_selecionado
        ).aggregate(total_aumento=Sum('valor_alterado'))

        contratos_novos = Contrato.objects.filter(
            flcancelado=False,
            data_contrato__year=ano_selecionado,
            data_contrato__month=mes_selecionado
        ).aggregate(total_novos=Sum('total_contrato'))


        # Obtém o valor total do aumento de contratos
        valor_aumento = eventos_aumento['total_aumento'] or 0

        # Obtém o valor total dos novos contratos
        valor_novos_contratos = contratos_novos['total_novos'] or 0

        meses = [calendar.month_name[i].capitalize() for i in range(1, 13)]
        anos = Contrato.objects.dates('data_instalacao', 'year').distinct()
        context = {
            'ano_selecionado': ano_selecionado,
            'mes_selecionado': mes_selecionado,
            'valor_aumento': valor_aumento,
            'valor_novos_contratos': valor_novos_contratos,
            'anos': anos,
            'meses': meses
        }

        return render(request, 'detalhes_aumento_contratos.html', context)

    # Obtém o ano atual
    meses = [calendar.month_name[i].capitalize() for i in range(1, 13)]
    anos = Contrato.objects.dates('data_instalacao', 'year').distinct()

    context = {'anos': anos, 'meses': meses}
    return render(request, 'detalhes_aumento_contratos.html', context)

@login_required_all
def excluir_contrato(request, id_contrato):
    contrato = Contrato.objects.get(id=id_contrato)

    if request.method == 'POST':
        contrato.delete()
        messages.success(request, 'Contrato excluído com sucesso.')
        return redirect('listar_contratos')

    context = {'contrato': contrato}
    return render(request, 'excluir_contrato.html', context)