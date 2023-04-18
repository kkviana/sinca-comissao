from django.shortcuts import render

from django.contrib import messages
    
def base(request):
    return render(request, 'base.html')

