from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def index(request):
    return render(request, 'index.html')

def usuario_login(request):
    if request.method == 'POST':
        username = request.POST.get('usuario')
        password = request.POST.get('senha')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            mensagem_erro = 'Usuário ou senha incorretos.'
            return render(request, 'login.html', {'mensagem_erro': mensagem_erro})
    else:
        return render(request, 'login.html')

def redirecionar_login(request):
    return redirect('login')