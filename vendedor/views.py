from django.shortcuts import render, redirect
from meuapp.utils import login_required_all
from .models import Vendedor
from .forms import VendedorForm


@login_required_all
def cadastrar_vendedor(request):
    if request.method == 'POST':
        form = VendedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_vendedores')
    else:
        form = VendedorForm()
    return render(request, 'cadastrar_vendedor.html', {'form': form})

@login_required_all
def lista_vendedores(request):
    vendedores = Vendedor.objects.filter(flinativo=False)
    return render(request, 'lista_vendedores.html', {'vendedores': vendedores})

def inativar_vendedor(request, id_vendedor):
    vendedor = Vendedor.objects.get(id=id_vendedor)
    vendedor.flinativo = True
    vendedor.save()
    return redirect('lista_vendedores')