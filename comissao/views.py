from decimal import Decimal
from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import Comissao
from contrato.models import Contrato
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect

def calcular_comissao_old(request):
    if request.method == 'POST':
        data = request.POST.get('mes_ano')

        contratos_selecionadas = request.POST.getlist('contratos')

        # Obter as contratos selecionadas
        contratos_do_mes = Contrato.objects.filter(pk__in=contratos_selecionadas)

        # Calcular o número total de contratos selecionadas do mês
        numero_contratos = contratos_do_mes.count()

        # Calcular o valor total das contratos selecionadas do mês
        valor_contratos = contratos_do_mes.aggregate(total=Sum('total_contrato'))['total'] or 0

        #Recuperar contratos totais
        contratos_totais = Contrato.objects.aggregate(total=Sum('total_contrato'))['total'] or 0

        # Calcular a comissão
        if numero_contratos < 10:
            comissao_acumulada = Decimal(contratos_totais) * Decimal(0.05)
            comissao_mes = Decimal(valor_contratos)
        elif 10 <= numero_contratos <= 20:
            comissao_acumulada = Decimal(valor_contratos) * Decimal(0.05)
            comissao_mes = Decimal(valor_contratos) * 2
        else:
            comissao_acumulada = Decimal(valor_contratos) * Decimal(0.05)
            comissao_mes = Decimal(valor_contratos) * 3

        # Criar um objeto Comissao com os valores calculados
        comissao = Comissao(
            data=data,
            quantidade_contratos=numero_contratos,
            valor_contratos_mes=valor_contratos,
            comissao_acumulada=comissao_acumulada,
            comissao_mes=comissao_mes,
            comissao_total=comissao_mes + comissao_acumulada
        )
        comissao.save()
        Contrato.objects.filter(pk__in=contratos_selecionadas).update(comissao_id=comissao.id)
        contratos = Contrato.objects.filter(comissao_id__isnull=True)
        return render(request, 'listar_contratos_comissao.html', {'contratos_totais': contratos_totais, 'contratos': contratos})
    else:
        data_atual = datetime.datetime.now()
        # Subtrai 1 mês da data atual para obter o mês anterior
        mes_anterior = data_atual.month - 1
        ano_atual = data_atual.year
        if mes_anterior == 0:
            # Caso especial: se o mês anterior for janeiro, ajusta o ano para o ano anterior
            mes_anterior = 12
            ano_atual -= 1

        # Passa a variável mes_anterior para o contexto do template
        mes_anterior = '{:02d}/{}'.format(mes_anterior, ano_atual)
        print(mes_anterior)
        contratos = Contrato.objects.filter(comissao_id__isnull=True)
        return render(request, 'listar_contratos_comissao.html', {'contratos': contratos, 'mes_anterior': mes_anterior})

def fechar_comissao(request):
    if request.method == 'POST':
        # Obtém a data selecionada no formulário como uma string
        data_str = request.POST.get('data')

        # Converte a string de data em um objeto date
        data = datetime.strptime(data_str, '%Y-%m').date()

        # Obtém todos os contratos do mês selecionado
        contratos_mes = Contrato.objects.filter(data_contrato__month=data.month, data_contrato__year=data.year, flcancelado=False)

        # Verifica se a data selecionada é o mês atual
        mes_atual = data == datetime.now().strftime('%Y-%m')

        # Verifica a quantidade de contratos do mês selecionado
        quantidade_contratos_mes = contratos_mes.count()
        todos_contratos = Contrato.objects.filter(flcancelado=False)

        # Verifica a quantidade de contratos feitos até o mês selecionado
        contratos_total = Contrato.objects.filter(data_contrato__lt=data, flcancelado=False).count()

        # Remove todos os registros de comissão existentes para o mês selecionado
        Comissao.objects.filter(data=data_str).delete()

        # Percorre todos os contratos do mês selecionado
        for contrato in todos_contratos:
            # Verifica se o contrato é de um mês anterior à data selecionada
            if contrato.data_contrato.month < data.month or contrato.data_contrato.year < data.year:
                # Atribui 5% do valor do contrato como comissão
                comissao_valor_contrato = contrato.total_contrato * Decimal('0.05')
            else:
                # Calcula a comissão com base na quantidade de contratos do mês
                if quantidade_contratos_mes < 10:
                    comissao_valor_contrato = contrato.total_contrato
                elif 10 <= quantidade_contratos_mes <= 20:
                    comissao_valor_contrato = contrato.total_contrato * 2
                else:
                    comissao_valor_contrato = contrato.total_contrato * 3

            # Cria uma nova instância de Comissao com os valores calculados para o contrato
            comissao = Comissao(data=data_str, valor_contrato_mes=comissao_valor_contrato, contrato=contrato)

            # Salva a comissão no banco de dados
            comissao.save()

        # Redireciona para a página de comissões
        return render(request, 'listar_comissoes.html')
    return render(request, 'fechar_comissao.html')

def calcular_comissao():
    # Obtém todas as comissões
    comissoes = Comissao.objects.all()

    # Cria um dicionário para armazenar os resultados por mês
    resultados = {}

    # Percorre todas as comissões
    for comissao in comissoes:
        # Obtém a data da comissão
        data = comissao.data

        # Obtém a quantidade de contratos para o mês da comissão
        contratos_mes = Comissao.objects.filter(data=data).count()

        # Obtém a quantidade total de contratos até o mês da comissão
        contratos_total = Comissao.objects.filter(data__lt=data).aggregate(total=Sum('valor_contrato_mes'))['total']

        # Verifica se contratos_total é None e atribui 0 a ele caso seja
        contratos_total = contratos_total if contratos_total is not None else 0

        # Calcula a comissão com base na quantidade de contratos do mês
        if contratos_mes < 10:
            comissao_valor = comissao.valor_contrato_mes + (contratos_total * Decimal('0.05'))
        elif 10 <= contratos_mes <= 20:
            comissao_valor = (comissao.valor_contrato_mes * 2) + (contratos_total * Decimal('0.05'))
        else:
            comissao_valor = (comissao.valor_contrato_mes * 3) + (contratos_total * Decimal('0.05'))

        # Armazena o resultado no dicionário
        resultados[data] = comissao_valor

    # Retorna o dicionário com os resultados
    return resultados

def listar_comissoes(request):
    # Agrupa as comissões por mês e soma seus valores
    comissoes = Comissao.objects.values('data', 'contrato__vendedor__nome').annotate(soma_comissao=Sum('valor_contrato_mes'))
    print (comissoes)
    return render(request, 'listar_comissoes.html', {'comissoes': comissoes})

