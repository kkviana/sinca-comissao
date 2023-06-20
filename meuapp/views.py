from django.shortcuts import render
from meuapp.utils import login_required_all
from django.contrib import messages

@login_required_all
def base(request):
    return render(request, 'base.html')

