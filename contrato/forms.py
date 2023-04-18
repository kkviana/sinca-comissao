from django import forms
from cliente.models import Cliente
from produto.models import Produto


class ItemVendaForm(forms.Form):
    produto = forms.ModelChoiceField(queryset=Produto.objects.all())
    quantidade = forms.IntegerField(min_value=1)
    preco_unitario = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01, widget=forms.TextInput(attrs={'readonly': 'readonly'}))


class VendaForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all())
    itens_venda = forms.Formset(field_classes=(ItemVendaForm,))
