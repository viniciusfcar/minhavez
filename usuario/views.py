from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Usuario
from .forms import FormUsuario
from .forms import FormUser
from django.contrib.auth.models import User
from ficha.models import Ficha
from fila.models import Fila
from consulta.models import Consulta
from autorizacao.models import Autorizacao
from exame.models import Exame
from agendamento.models import Agendamento
from rolepermissions.roles import assign_role
from rest_framework import viewsets
from .serializers import UsuarioSerializer, UserSerializer
from rolepermissions.checkers import has_permission
from rest_framework.decorators import action
from rest_framework.response import Response
import json
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework.filters import SearchFilter


class GetUsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer  
    filter_backends = (SearchFilter,)
    search_fields = ['=cpf', '=sus']

    def get_queryset(self):
        queryset = Usuario.objects.all()
        return queryset

    @action(methods=['get'], detail=True)
    def minhasFichas(self, request, pk=None):
        usuario = get_object_or_404(Usuario, pk=pk)
        fichas = Ficha.objects.filter(usuario=usuario).order_by('status')
        tmpJson = serializers.serialize("json", fichas)
        tmpObj = json.loads(tmpJson)
        return HttpResponse(json.dumps(tmpObj))
    

    @action(methods=['post'], detail=False)
    def verificaUser(self, request):
        token = request.POST.get('token')
        user = User.objects.filter(auth_token=token)
        usuario = Usuario.objects.filter(user=user[0])
        tmpJson = serializers.serialize("json", usuario)
        tmpObj = json.loads(tmpJson)
        return HttpResponse(json.dumps(tmpObj))

    @action(methods=['post'], detail=False)
    def set_notificacao(self, request):
        token = request.POST.get('token')
        token = token.replace('"', '')
        user = User.objects.filter(auth_token=token)
        usuario = Usuario.objects.filter(user=user[0])
        if usuario:
            if request.method == 'POST':
                usuario[0].notificacao = request.POST.get('notificacao')
                usuario[0].save()
                return HttpResponse(status=status.HTTP_200_OK)
            else:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        else:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)


    @action(methods=['post'], detail=False)
    def cadastro_user(self, request):
        new_user = User.objects.filter(username=request.POST.get('username'))
        user_cpf = Usuario.objects.filter(cpf=request.POST.get('cpf'))
        user_sus = Usuario.objects.filter(sus=request.POST.get('sus'))

        if request.method == 'POST':
            try:
                validate_email(request.POST.get('email'))
                valid_email = True
            except ValidationError:
                valid_email = False

            if valid_email:
                if not new_user and not user_cpf and not user_sus:
                    password = request.POST.get('password')

                    usuario = Usuario(cpf=request.POST.get('cpf'), rg=request.POST.get('rg'), sus=request.POST.get('sus'),
                                    logradouro=request.POST.get('logradouro'), cep=request.POST.get('cep'), sexo=request.POST.get('sexo'),
                                    numero=request.POST.get('numero'), complemento=request.POST.get('complemento'), telefone=request.POST.get('telefone'),
                                    bairro=request.POST.get('bairro'), cidade=request.POST.get('cidade'), estado=request.POST.get('estado'))

                    user = User(username=request.POST.get('username'), first_name=request.POST.get('first_name'),
                                last_name=request.POST.get('last_name'), email=request.POST.get('email'))

                    user.set_password(password)
                    user.save()
                    usuario.user = user
                    usuario.save()
                    Token.objects.create(user=user)
                    assign_role(user, 'usuario')
                    return HttpResponse(status=status.HTTP_200_OK)
                else:
                    return HttpResponse(status=status.HTTP_409_CONFLICT)
            else:
                return HttpResponse(status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False)
    def editar_perfil(self, request):
        token = request.POST.get('token')
        token = token.replace('"', '')
        user = User.objects.filter(auth_token=token)
        usuario = Usuario.objects.filter(user=user[0])

        if user and usuario:
            try:
                validate_email(request.POST.get('email'))
                valid_email = True
            except ValidationError:
                valid_email = False

            if valid_email:
                new_user = User.objects.filter(username=request.POST.get('username'))
                user_cpf = Usuario.objects.filter(cpf=request.POST.get('cpf'))
                user_sus = Usuario.objects.filter(sus=request.POST.get('sus'))

                if new_user[0] == None or new_user[0] == user[0]:
                    if user_cpf[0] == None or user_cpf[0].user == user[0]:
                        if user_sus[0] == None or user_sus[0].user == user[0]:
                            user[0].username = request.POST.get('username')
                            user[0].first_name = request.POST.get('first_name')
                            user[0].email = request.POST.get('email')
                            user[0].last_name = request.POST.get('last_name')
                            usuario[0].cpf = request.POST.get('cpf')
                            usuario[0].rg = request.POST.get('rg')
                            usuario[0].sus = request.POST.get('sus')
                            usuario[0].rua = request.POST.get('rua')
                            usuario[0].numero = request.POST.get('numero')
                            usuario[0].complemento = request.POST.get('complemento')
                            usuario[0].bairro = request.POST.get('bairro')
                            usuario[0].cidade = request.POST.get('cidade')
                            usuario[0].estado = request.POST.get('estado')
                            user[0].save()
                            usuario[0].save()
                            return HttpResponse(status=status.HTTP_200_OK)
                        else:
                            return HttpResponse(status=status.HTTP_409_CONFLICT)
                    else:
                        return HttpResponse(status=status.HTTP_409_CONFLICT)
                else:
                    return HttpResponse(status=status.HTTP_409_CONFLICT)
            else:
                return HttpResponse(status=status.HTTP_406_NOT_ACCEPTABLE)        
        else:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

class GetUserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer  
    filter_backends = (SearchFilter,)
    search_fields = ['=username']

    def get_queryset(self):
        queryset = User.objects.all()
        return queryset

def cadastroUsuario(request):

    form = FormUsuario()
    context = {
        'form': form,
    }

    if request.method == 'POST':
        
        user = Usuario.objects.filter(user__username=request.POST.get('username'))

        if user:

            context = {
                'form': FormUsuario(),
                'username': request.POST.get('username'),
                'email': request.POST.get('email'),
                'nome': request.POST.get('firstname'),
                'sobrenome': request.POST.get('lastname'),
                'rua': request.POST.get('rua'),
                'numero': request.POST.get('numero'),
                'bairro': request.POST.get('bairro'),
                'cidade': request.POST.get('cidade'),
                'complemento': request.POST.get('completo'),
                'estado': request.POST.get('estado'),
                'cpf': request.POST.get('cpf'),
                'sus': request.POST.get('sus'),
                'sexo': request.POST.get('sexo'),
                'rg': request.POST.get('rg'),
                'msg_error': 'Já existe usuario com esse username, escolha outro'
            }

            return render(request, 'cadastro_usuario.html', {'context': context})
        else:
            password = request.POST.get('password')

            usuario = Usuario(cpf=request.POST.get('cpf'), rg=request.POST.get('rg'), sus=request.POST.get('sus'),
                            logradouro=request.POST.get('logradouro'), cep=request.POST.get('cep'), sexo=request.POST.get('sexo'),
                            numero=request.POST.get('numero'), complemento=request.POST.get('complemento'), telefone=request.POST.get('telefone'),
                            bairro=request.POST.get('bairro'), cidade=request.POST.get('cidade'), estado=request.POST.get('estado'))

            user = User(username=request.POST.get('username'), first_name=request.POST.get('firstname'),
                        last_name=request.POST.get('lastname'), email=request.POST.get('email'))

            user.set_password(password)
            user.save()
            usuario.user = user
            usuario.save()
            Token.objects.create(user=user)
            assign_role(user, 'usuario')
            
            return redirect('/')

    return render(request, 'cadastro_usuario.html', {'context': context})


@login_required(login_url='/accounts/login')
def listaUsuario(request):
    usuarios = Usuario.objects.all()

    return render(request, 'lista_usuario.html', {'atendimentos': usuarios})


@login_required(login_url='/accounts/login')
def alterarPerfil(request, id):
    if has_permission(request.user, 'permissao_usuario'):
        usuario = get_object_or_404(Usuario, pk=id)
        form = FormUsuario(request.POST or None, request.FILES or None, instance=usuario)

        context = {
            'form': form,
            'usuario': usuario
        }

        if request.method == 'POST':
            usuario.user.username = request.POST.get('username')
            usuario.user.email = request.POST.get('email')
            usuario.user.first_name = request.POST.get('firstname')
            usuario.user.last_name = request.POST.get('lastname')
            usuario.logradouro = request.POST.get('logradouro')
            usuario.bairro = request.POST.get('bairro')
            usuario.numero = request.POST.get('numero')
            usuario.cidade = request.POST.get('cidade')
            usuario.estado = request.POST.get('estado')
            usuario.rg = request.POST.get('rg')
            usuario.cpf = request.POST.get('cpf')
            usuario.sexo = request.POST.get('sexo')
            usuario.sus = request.POST.get('sus')
            usuario.save()
            if form.is_valid():
                form.save()
            return render(request, 'perfil_usuario.html', {'usuario': usuario})

        return render(request, 'alterar_perfil.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home.html', {'context': context})


@login_required(login_url='/accounts/login')
def deleteUsuario(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    form = FormUsuario(request.POST or None, request.FILES or None, instance=usuario)

    if request.method == 'POST':
        usuario.delete()
        return redirect('listaUsuario')

    return render(request, 'delete_usuario.html', {'nome': usuario.nome})


@login_required(login_url='/accounts/login')
def detalhesUsuario(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        usuario = get_object_or_404(Usuario, pk=id)

        return render(request, 'detalhes_usuario.html', {'usuario': usuario})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})


@login_required(login_url='/accounts/login')
def minhasFichas(request):
    if has_permission(request.user, 'permissao_usuario'):
        usuario = Usuario.objects.filter(user=request.user)
        fichas = Ficha.objects.filter(usuario=usuario[0]).order_by('status')
        pesquisa = request.GET.get('pesquisa')

        if pesquisa:
            fichas = fichas.filter(numero__icontains=pesquisa).order_by('status') | fichas.filter(status__icontains=pesquisa).order_by('status')

            if fichas:
                context = {
                    'fichas': fichas,
                }

            else:
                fichas = Ficha.objects.filter(usuario=usuario[0]).order_by('status')
                context = {
                    'fichas': fichas,
                    'msg_busca': 'Nada encontrado para esses parâmetros!'
                }

        elif fichas:

            context = {
                'fichas': fichas,
            }

        else:
            context = {
                'msg_alert': 'Você não possue nenhuma ficha!'
            }

        return render(request, 'minhas_fichas.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home.html', {'context': context})


@login_required(login_url='/accounts/login')
def meusAgendamentos(request):
    if has_permission(request.user, 'permissao_usuario'):
        usuario = Usuario.objects.filter(user=request.user)
        agendamentos = Agendamento.objects.filter(usuarios=usuario[0])
        nome = request.GET.get('nome')
        
        if nome:
            agendamentos = agendamentos.filter(nome__icontains=nome)

            if agendamentos:
                context = {
                    'agendamentos': agendamentos
                }
            else:
                agendamentos = Agendamento.objects.filter(usuarios=usuario[0])
                context = {
                    'agendamentos': agendamentos,
                    'msg_busca': 'Nada encontrado para esses parâmetros!'
                }

        elif agendamentos:
            context = {
                'agendamentos': agendamentos
            }

        else:
            context = {
                'msg_alert': 'Você não participa de nenhum agendamento!'
            }

        return render(request, 'meus_agendamentos.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home.html', {'context': context})


@login_required(login_url='/accounts/login')
def perfilUsuario(request):
    if has_permission(request.user, 'permissao_usuario'):
        usuario = Usuario.objects.filter(user=request.user)

        return render(request, 'perfil_usuario.html', {'usuario': usuario[0]})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home.html', {'context': context})

