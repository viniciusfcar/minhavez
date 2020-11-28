from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate,
    get_user_model,
)
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from unidadeSaude.models import UnidadeSaude
from usuario.models import Usuario
from rolepermissions.checkers import has_permission

def login(request):

    username = request.POST.get('username')
    password = request.POST.get('password')

    if request.method == 'POST':

        try:
            user = User.objects.get(username=username)

            if user is None:
                msg_error = 'Usuário inválido(s)'
                return render(request, 'login.html', {'msg_error': msg_error})
            else:

                if not user.check_password(password):
                    msg_error = 'Senha inválida'
                    return render(request, 'login.html', {'msg_error': msg_error})
                else:
                    user = authenticate(username=username, password=password)
                    auth_login(request, user)
                    
                    if has_permission(user, 'permissao_usuario'):
                        return redirect('homeUsuario')
                    
                    elif has_permission(user, 'permissao_unidade'):
                        return redirect('homeUnidadeSaude')
                    
                    else:
                        return redirect('homeAdm')
        except Exception:
            msg_error = 'Usuário e/ou Senha inválido(s)'
            return render(request, 'login.html', {'msg_error': msg_error})

    return render(request, 'login.html')

def logout(request):
    auth_logout(request)
    return redirect('/')



