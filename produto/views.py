from django.shortcuts import render, redirect, get_object_or_404
from meuapp.utils import login_required_all
from .forms import ProdutoForm
from .models import Produto


@login_required_all
def cadastrar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_produtos')
    return render(request, 'cadastrar_produto.html')

@login_required_all
def lista_produtos(request):
    produtos = Produto.objects.filter(flinativo=False)
    return render(request, 'lista_produtos.html', {'produtos': produtos})

@login_required_all
def editar_produto(request, id_produto):
    produto = get_object_or_404(Produto, id=id_produto)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('lista_produtos')
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'editar_produto.html', {'form': form, 'produto': produto})

@login_required_all
def inativar_produto(request, id_produto):
    produto = Produto.objects.get(id=id_produto)
    produto.flinativo = True
    produto.save()
    return redirect('lista_produtos')