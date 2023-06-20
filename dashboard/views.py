from django.shortcuts import render
from contrato.models import Contrato
from contrato.models import ContratoEvento
from vendedor.models import Vendedor
from django.db import models
import calendar
import locale
from django.http import JsonResponse
from django.db.models.functions import TruncMonth, TruncYear
from django.db.models import Count, Sum, Q, Subquery, OuterRef, IntegerField
import random
import math
from datetime import date
from itertools import groupby
from django.views.decorators.http import require_GET
from django.db.models.functions import ExtractMonth, ExtractYear
from meuapp.utils import login_required_all


locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

@login_required_all
def dashboard_contratos(request):
    # Query para buscar os dados de venda por mês
    vendas_por_mes = Contrato.objects.values('data_instalacao__month') \
                        .annotate(numero_vendas=models.Count('id')) \
                        .order_by('data_instalacao__month')
    
    vendas_por_mes_valor = Contrato.objects.values('data_instalacao__month') \
                        .annotate(valor_vendas=models.Sum('total_contrato')) \
                        .order_by('data_instalacao__month')
    
    vendas_por_ano = Contrato.objects.values('data_instalacao__year') \
                        .annotate(numero_vendas=models.Count('id')) \
                        .order_by('data_instalacao__year')
    
    vendas_por_ano_valor = Contrato.objects.values('data_instalacao__year') \
        .annotate(valor_vendas=models.Sum('total_contrato')) \
        .order_by('data_instalacao__year')
    
    cancelamentos_por_mes = ContratoEvento.objects.filter(evento_tipo_id=4) \
        .values('evento_data__month') \
        .annotate(numero_cancelamentos=Count('id')) \
        .order_by('evento_data__month')
    
    cancelamentos_por_mes_valor = ContratoEvento.objects.filter(evento_tipo_id=4) \
        .values('evento_data__month') \
        .annotate(valor_cancelamentos=Sum('contrato__total_contrato')) \
        .order_by('evento_data__month')
    
    cancelamentos_por_ano = ContratoEvento.objects.filter(evento_tipo_id=4) \
        .values('evento_data__year') \
        .annotate(numero_cancelamentos=Count('id')) \
        .order_by('evento_data__year')
    
    cancelamentos_por_ano_valor = ContratoEvento.objects.filter(evento_tipo_id=4) \
        .values('evento_data__year') \
        .annotate(valor_cancelamentos=Sum('contrato__total_contrato')) \
        .order_by('evento_data__year')
    
    saldo_por_ano = []
    saldo_acumulado = 0
    for venda in vendas_por_ano:
        ano = venda['data_instalacao__year']
        numero_vendas = venda['numero_vendas']
        numero_cancelamentos = cancelamentos_por_ano.filter(evento_data__year=ano).values('numero_cancelamentos').first()
        if numero_cancelamentos:
            numero_cancelamentos = numero_cancelamentos['numero_cancelamentos']
        else:
            numero_cancelamentos = 0
        saldo = numero_vendas - numero_cancelamentos
        saldo_acumulado += saldo
        saldo_por_ano.append({'ano': ano, 'saldo': saldo, 'saldo_acumulado': saldo_acumulado})


    saldo_por_ano_valor = []
    saldo_acumulado_valor = 0
    for venda in vendas_por_ano_valor:
        ano = venda['data_instalacao__year']
        valor_vendas = venda['valor_vendas']
        valor_cancelamentos = cancelamentos_por_ano_valor.filter(evento_data__year=ano).values('valor_cancelamentos').first()
        if valor_cancelamentos:
            valor_cancelamentos = valor_cancelamentos['valor_cancelamentos']
        else:
            valor_cancelamentos = 0
        saldo = valor_vendas - valor_cancelamentos
        saldo_acumulado_valor += saldo
        saldo_por_ano_valor.append({'ano': ano, 'saldo': saldo, 'saldo_acumulado_valor': saldo_acumulado_valor})

    meses = [calendar.month_name[i].capitalize() for i in range(1, 13)]
    anos = Contrato.objects.dates('data_instalacao', 'year').distinct()

    context = {
        'saldo_por_ano_valor': saldo_por_ano_valor,
        'saldo_por_ano': saldo_por_ano,
        'cancelamentos_por_ano_valor': cancelamentos_por_ano_valor,
        'cancelamentos_por_mes_valor': cancelamentos_por_mes_valor,
        'vendas_por_ano_valor': vendas_por_ano_valor,
        'vendas_por_mes_valor': vendas_por_mes_valor,
        'cancelamentos_por_mes': cancelamentos_por_mes,
        'cancelamentos_por_ano': cancelamentos_por_ano,
        'anos': anos,
        'meses': meses,
        'vendas_por_mes': vendas_por_mes,
        'vendas_por_ano': vendas_por_ano,
    }
    return render(request, 'dashboard_contratos.html', context)

@login_required_all    
def vendas_por_mes_ano(request, ano):
    # Verifica se o ano informado é válido
    try:
        ano = int(ano)
    except ValueError:
        return JsonResponse({'erro': 'Ano inválido.'}, status=400)

    if ano < 2000 or ano > 2100:
        return JsonResponse({'erro': 'Ano inválido.'}, status=400)

    # Faz a query para buscar as vendas por mês do ano informado
    vendas_por_mes = Contrato.objects.filter(data_instalacao__year=ano) \
                        .annotate(mes=TruncMonth('data_instalacao')) \
                        .values('mes') \
                        .annotate(numero_vendas=Count('id')) \
                        .order_by('mes')

    # Cria uma lista com o número de vendas para cada mês do ano informado
    vendas_por_mes_ano = [0] * 12
    for venda in vendas_por_mes:
        mes = venda['mes'].month - 1
        vendas_por_mes_ano[mes] = venda['numero_vendas']

    # Cria uma lista com os nomes dos meses do ano informado
    meses_ano = [calendar.month_name[i].capitalize() for i in range(1, 13)]

    # Retorna os dados em formato JSON
    data = {
        'labels': meses_ano,
        'data': vendas_por_mes_ano
    }
    return JsonResponse(data)

@login_required_all
def vendas_por_mes_ano_valor(request, ano):
    # Verifica se o ano informado é válido
    try:
        ano = int(ano)
    except ValueError:
        return JsonResponse({'erro': 'Ano inválido.'}, status=400)

    if ano < 2000 or ano > 2100:
        return JsonResponse({'erro': 'Ano inválido.'}, status=400)

    # Faz a query para buscar as vendas por mês do ano informado
    vendas_por_mes_valor = Contrato.objects.filter(data_instalacao__year=ano) \
                        .annotate(mes=TruncMonth('data_instalacao')) \
                        .values('mes') \
                        .annotate(valor_vendas=Sum('total_contrato')) \
                        .order_by('mes')

    # Cria uma lista com o número de vendas para cada mês do ano informado
    vendas_por_mes_ano_valor = [0] * 12
    for venda in vendas_por_mes_valor:
        mes = venda['mes'].month - 1
        vendas_por_mes_ano_valor[mes] = venda['valor_vendas']

    # Cria uma lista com os nomes dos meses do ano informado
    meses_ano = [calendar.month_name[i].capitalize() for i in range(1, 13)]

    # Retorna os dados em formato JSON
    data = {
        'labels': meses_ano,
        'data': vendas_por_mes_ano_valor
    }
    return JsonResponse(data)

@login_required_all
def cancelamentos_por_mes_ano(request, ano):
    # Verifica se o ano informado é válido
    try:
        ano = int(ano)
    except ValueError:
        return JsonResponse({'erro': 'Ano inválido.'}, status=400)

    if ano < 2000 or ano > 2100:
        return JsonResponse({'erro': 'Ano inválido.'}, status=400)

    # Faz a query para buscar as vendas por mês do ano informado
    cancelamentos_por_mes = ContratoEvento.objects.filter(evento_data__year=ano, evento_tipo_id=4) \
        .annotate(mes=TruncMonth('evento_data')) \
        .values('mes') \
        .annotate(numero_cancelamentos=Count('id')) \
        .order_by('mes')

    # Cria uma lista com o número de vendas para cada mês do ano informado
    cancelamentos_por_mes_ano = [0] * 12
    for cancelamento in cancelamentos_por_mes:
        mes = cancelamento['mes'].month - 1
        cancelamentos_por_mes_ano[mes] = cancelamento['numero_cancelamentos']

    # Cria uma lista com os nomes dos meses do ano informado
    meses_ano = [calendar.month_name[i].capitalize() for i in range(1, 13)]

    # Retorna os dados em formato JSON
    data = {
        'labels': meses_ano,
        'data': cancelamentos_por_mes_ano
    }
    return JsonResponse(data)

@login_required_all
def cancelamentos_por_mes_ano_valor(request, ano):
    # Verifica se o ano informado é válido
    try:
        ano = int(ano)
    except ValueError:
        return JsonResponse({'erro': 'Ano inválido.'}, status=400)

    if ano < 2000 or ano > 2100:
        return JsonResponse({'erro': 'Ano inválido.'}, status=400)

    # Faz a query para buscar as vendas por mês do ano informado
    cancelamentos_por_mes_valor = ContratoEvento.objects.filter(evento_data__year=ano, evento_tipo_id=4) \
        .annotate(mes=TruncMonth('evento_data')) \
        .values('mes') \
        .annotate(valor_cancelamentos=Sum('contrato__total_contrato')) \
        .order_by('mes')

    # Cria uma lista com o número de vendas para cada mês do ano informado
    cancelamentos_por_mes_ano_valor = [0] * 12
    for cancelamento in cancelamentos_por_mes_valor:
        mes = cancelamento['mes'].month - 1
        cancelamentos_por_mes_ano_valor[mes] = cancelamento['valor_cancelamentos']

    # Cria uma lista com os nomes dos meses do ano informado
    meses_ano = [calendar.month_name[i].capitalize() for i in range(1, 13)]

    # Retorna os dados em formato JSON
    data = {
        'labels': meses_ano,
        'data': cancelamentos_por_mes_ano_valor
    }
    return JsonResponse(data)

@login_required_all
def saldo_por_mes_ano_valor(request, ano):
    # Verifica se o ano informado é válido
    try:
        ano = int(ano)
    except ValueError:
        return JsonResponse({'erro': 'Ano inválido.'}, status=400)

    if ano < 2000 or ano > 2100:
        return JsonResponse({'erro': 'Ano inválido.'}, status=400)

    # Faz a query para buscar as vendas por mês do ano informado
    vendas_por_mes = Contrato.objects.filter(data_instalacao__year=ano) \
                        .annotate(mes=TruncMonth('data_instalacao')) \
                        .values('mes') \
                        .annotate(valor_vendas=Sum('total_contrato')) \
                        .order_by('mes')

    # Faz a query para buscar os cancelamentos por mês do ano informado
    cancelamentos_por_mes = ContratoEvento.objects.filter(evento_data__year=ano, evento_tipo_id=4) \
        .annotate(mes=TruncMonth('evento_data')) \
        .values('mes') \
        .annotate(valor_cancelamentos=Sum('contrato__total_contrato')) \
        .order_by('mes')

    # Cria uma lista com o saldo para cada mês do ano informado
    saldo_por_mes_ano = [0] * 12
    for venda in vendas_por_mes:
        mes = venda['mes'].month - 1
        saldo_por_mes_ano[mes] += venda['valor_vendas']
    for cancelamento in cancelamentos_por_mes:
        mes = cancelamento['mes'].month - 1
        saldo_por_mes_ano[mes] -= cancelamento['valor_cancelamentos']

    # Cria uma lista com os nomes dos meses do ano informado
    meses_ano = [calendar.month_name[i].capitalize() for i in range(1, 13)]

    # Retorna os dados em formato JSON
    data = {
        'labels': meses_ano,
        'data': saldo_por_mes_ano
    }
    return JsonResponse(data)

@login_required_all
def saldo_por_mes_ano(request, ano):
    # Verifica se o ano informado é válido
    try:
        ano = int(ano)
    except ValueError:
        return JsonResponse({'erro': 'Ano inválido.'}, status=400)

    if ano < 2000 or ano > 2100:
        return JsonResponse({'erro': 'Ano inválido.'}, status=400)

    # Faz a query para buscar as vendas por mês do ano informado
    vendas_por_mes = Contrato.objects.filter(data_instalacao__year=ano) \
                        .annotate(mes=TruncMonth('data_instalacao')) \
                        .values('mes') \
                        .annotate(numero_vendas=Count('id')) \
                        .order_by('mes')

    # Faz a query para buscar os cancelamentos por mês do ano informado
    cancelamentos_por_mes = ContratoEvento.objects.filter(evento_data__year=ano, evento_tipo_id=4) \
        .annotate(mes=TruncMonth('evento_data')) \
        .values('mes') \
        .annotate(numero_cancelamentos=Count('id')) \
        .order_by('mes')

    # Cria uma lista com o saldo para cada mês do ano informado
    saldo_por_mes = []
    saldo_acumulado = 0
    for venda in vendas_por_mes:
        mes = venda['mes'].month
        numero_vendas = venda['numero_vendas']
        numero_cancelamentos = cancelamentos_por_mes.filter(mes__month=mes).values('numero_cancelamentos').first()
        if numero_cancelamentos:
            numero_cancelamentos = numero_cancelamentos['numero_cancelamentos']
        else:
            numero_cancelamentos = 0
        saldo = numero_vendas - numero_cancelamentos
        saldo_acumulado += saldo
        saldo_por_mes.append({'mes': mes, 'saldo': saldo, 'saldo_acumulado': saldo_acumulado})

    # Cria uma lista com os nomes dos meses do ano informado
    meses_ano = [calendar.month_name[i].capitalize() for i in range(1, 13)]

    # Retorna os dados em formato JSON
    data = {
        'labels': meses_ano,
        'data': [saldo['saldo'] for saldo in saldo_por_mes],
        'saldo_acumulado': [saldo['saldo_acumulado'] for saldo in saldo_por_mes]
    }
    return JsonResponse(data)

@login_required_all
def dashboard_vendedores(request):
    vendas_por_mes_por_vendedor = Contrato.objects.values('data_instalacao__year', 'data_instalacao__month', 'vendedor') \
    .annotate(numero_vendas=Count('id'), valor_vendas=Sum('total_contrato')) \
    .order_by('data_instalacao__year', 'data_instalacao__month', 'vendedor')

    anos = set([v['data_instalacao__year'] for v in vendas_por_mes_por_vendedor])
    vendedores = Vendedor.objects.all()
    vendas_por_ano_por_vendedor = []
    
    for vendedor in vendedores:
        vendas_vendedor_por_ano = {}
        for ano in anos:
            vendas_vendedor_por_ano[ano] = {'numero_vendas': 0, 'valor_vendas': 0}
        for venda in vendas_por_mes_por_vendedor.filter(vendedor__id=vendedor.id):
            ano = venda['data_instalacao__year']
            vendas_vendedor_por_ano[ano]['numero_vendas'] += venda['numero_vendas']
            vendas_vendedor_por_ano[ano]['valor_vendas'] += venda['valor_vendas']
        for ano, vendas in vendas_vendedor_por_ano.items():
            vendas_por_ano_por_vendedor.append({'vendedor': vendedor.nome, 'data_instalacao__year': ano, 'numero_vendas': vendas['numero_vendas'], 'valor_vendas': vendas['valor_vendas']})


    anos = Contrato.objects.dates('data_instalacao', 'year').distinct()
    meses = [calendar.month_name[i].capitalize() for i in range(1, 13)]
    context = {
        'ano': ano,
        'meses': meses,
        'anos': anos,
        'vendas_por_mes_por_vendedor': vendas_por_mes_por_vendedor,
        'vendas_por_ano_por_vendedor': vendas_por_ano_por_vendedor,
    }
    return render(request, 'dashboard_vendedores.html', context)

@login_required_all
def vendas_por_mes_vendedor(request, ano):
    ano = int(ano)
    vendas_por_mes = Contrato.objects \
        .annotate(mes=ExtractMonth('data_instalacao')) \
        .filter(data_instalacao__year=ano) \
        .values('mes', 'vendedor__nome') \
        .annotate(numero_vendas=Count('id')) \
        .order_by('mes', 'vendedor')
    
    # Cria um dicionário para armazenar as vendas por vendedor
    vendas_por_vendedor = {}
    
    for venda in vendas_por_mes:
        mes = venda['mes']
        vendedor = venda['vendedor__nome']
        numero_vendas = venda['numero_vendas']
        
        # Adiciona o número de vendas ao dicionário correspondente ao vendedor e ao mês
        if vendedor not in vendas_por_vendedor:
            vendas_por_vendedor[vendedor] = {
                'label': vendedor,
                'data': [0] * 12
            }
        vendas_por_vendedor[vendedor]['data'][mes-1] = numero_vendas
    
    # Cria os datasets para cada vendedor
    datasets = [vendas_por_vendedor[vendedor] for vendedor in vendas_por_vendedor]
    
    # Cria o dicionário de dados para o gráfico
    data = {
        'labels': [calendar.month_name[mes] for mes in range(1, 13)],
        'datasets': datasets
    }
    
    return JsonResponse(data)

@login_required_all
def vendas_por_mes_vendedor_valor(request, ano):
    ano = int(ano)
    vendas_por_mes = Contrato.objects \
        .annotate(mes=ExtractMonth('data_instalacao')) \
        .filter(data_instalacao__year=ano) \
        .values('mes', 'vendedor__nome') \
        .annotate(valor_vendas=models.Sum('total_contrato')) \
        .order_by('mes', 'vendedor')
    
    # Cria um dicionário para armazenar as vendas por vendedor
    vendas_por_vendedor = {}
    
    for venda in vendas_por_mes:
        mes = venda['mes']
        vendedor = venda['vendedor__nome']
        valor_vendas = venda['valor_vendas']
        
        # Adiciona o número de vendas ao dicionário correspondente ao vendedor e ao mês
        if vendedor not in vendas_por_vendedor:
            vendas_por_vendedor[vendedor] = {
                'label': vendedor,
                'data': [0] * 12
            }
        vendas_por_vendedor[vendedor]['data'][mes-1] = valor_vendas
    
    # Cria os datasets para cada vendedor
    datasets = [vendas_por_vendedor[vendedor] for vendedor in vendas_por_vendedor]
    
    # Cria o dicionário de dados para o gráfico
    data = {
        'labels': [calendar.month_name[mes] for mes in range(1, 13)],
        'datasets': datasets
    }
    
    return JsonResponse(data)

