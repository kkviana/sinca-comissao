from django.shortcuts import render, redirect, get_object_or_404
from meuapp.utils import login_required_all
from .models import Cliente
from .forms import ClienteForm


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

def inativar_cliente(request, id_cliente):
    cliente = Cliente.objects.get(id=id_cliente)
    cliente.flinativo = True
    cliente.save()
    return redirect('lista_clientes') # Redirecionar para a página do cliente
    
    
