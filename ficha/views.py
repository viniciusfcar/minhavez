from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from fila.models import Fila
from ficha.models import Ficha
from usuario.models import Usuario
from django.contrib.auth.models import User
from consulta.models import Consulta
from agendamento.models import Agendamento
from .forms import FormFicha
from autorizacao.models import Autorizacao
from unidadeSaude.models import UnidadeSaude
from exame.models import Exame
from rest_framework import viewsets
from .serializers import FichaSerializer
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from weasyprint import HTML
from rolepermissions.checkers import has_permission
from rest_framework.decorators import action
from rest_framework.response import Response
import json
from django.core import serializers
from rest_framework import status

class GetFichaViewSet(viewsets.ModelViewSet):
    serializer_class = FichaSerializer

    def get_queryset(self):
        queryset = Ficha.objects.all()
        return queryset

    @action(methods=['get'], detail=True)
    def consulta_posicao_ficha(self, request, pk=None):
        ficha = get_object_or_404(Ficha, pk=pk)
        filas = Fila.objects.filter(fichas=ficha)
        posicao = 0

        if filas:
            if filas[0].fichas.all():
                for fic in filas[0].fichas.all():
                    if fic == ficha:  
                        return HttpResponse(json.dumps(posicao))
                    else:
                        posicao += 1
            else:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        else:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False)
    def cadastro_ficha_consulta(self, request):
        consulta = get_object_or_404(Consulta, pk=request.POST.get('id_consulta'))
        token = request.POST.get('token')
        token = token.replace('"', '')

        if token:
            user = User.objects.filter(auth_token=token)
            usuario = Usuario.objects.filter(user=user[0])
            permitido = True
            agendado = False
            fila_normal = None
            fila_preferencial = None
            num1 = 1
            num2 = 1
            if request.method == 'POST':
                if consulta.create_fila:
                    
                    for fila in consulta.filas.all():
                        if fila.fila_preferencial:
                            fila_preferencial = fila
                        else:
                            fila_normal = fila

                    for ficha in fila_normal.fichas.all():
                        if ficha.usuario == usuario[0]:
                            permitido = False
                        num1 = 1 + ficha.numero

                    for ficha in fila_preferencial.fichas.all():
                        if ficha.usuario == usuario[0]:
                            permitido = False
                        num2 = 1 + ficha.numero

                    if consulta.agendamento and consulta.agendamento.usuarios:
                        for user in consulta.agendamento.usuarios.all():
                            if user == usuario[0]:
                                agendado = True

                    if permitido:

                        preferencial = None

                        if request.POST.get('preferencial') == 0:
                            preferencial = False
                        else:
                            preferencial = True                        

                        if preferencial:
                            ficha = Ficha()
                            ficha.numero = num2
                            ficha.preferencial = preferencial
                            ficha.usuario = usuario[0]
                            ficha.status = "AGUARDANDO"
                            ficha.save()
                            fila_preferencial.fichas.add(ficha)
                            
                            if agendado == False:
                                fila_preferencial.vagas -= 1
                                fila_normal.vagas -= 1
                            fila_preferencial.save()
                            fila_normal.save()

                        else:
                            ficha = Ficha()
                            ficha.numero = num1
                            ficha.preferencial = preferencial
                            ficha.usuario = usuario[0]
                            ficha.status = "AGUARDANDO"
                            ficha.save()
                            fila_normal.fichas.add(ficha)

                            if agendado == False:
                                fila_normal.vagas -= 1
                                fila_preferencial.vagas -= 1
                            fila_normal.save()
                            fila_preferencial.save()
                        fichas = []
                        fichas.append(ficha)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
                        tmpJson = serializers.serialize("json", fichas)
                        tmpObj = json.loads(tmpJson)  
                        return HttpResponse(json.dumps(tmpObj))
                    else:
                        return HttpResponse(status=status.HTTP_403_FORBIDDEN)
                else:
                    return HttpResponse(status=status.HTTP_403_FORBIDDEN)
            else:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        else:
            return HttpResponse(status=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED)
    
    @action(methods=['post'], detail=False)
    def cadastro_ficha_autorizacao(self, request):
        autorizacao = get_object_or_404(Autorizacao, pk=request.POST.get('id_autorizacao'))
        token = request.POST.get('token')
        token = token.replace('"', '')

        if token:
            user = User.objects.filter(auth_token=token)
            usuario = Usuario.objects.filter(user=user[0])
            permitido = True
            agendado = False
            fila_normal = None
            fila_preferencial = None
            num1 = 1
            num2 = 1
            if request.method == 'POST':
                if autorizacao.create_fila:
                    
                    for fila in autorizacao.filas.all():
                        if fila.fila_preferencial:
                            fila_preferencial = fila
                        else:
                            fila_normal = fila

                    for ficha in fila_normal.fichas.all():
                        if ficha.usuario == usuario[0]:
                            permitido = False
                        num1 = 1 + ficha.numero

                    for ficha in fila_preferencial.fichas.all():
                        if ficha.usuario == usuario[0]:
                            permitido = False
                        num2 = 1 + ficha.numero

                    if autorizacao.agendamento and autorizacao.agendamento.usuarios:
                        for user in autorizacao.agendamento.usuarios.all():
                            if user == usuario[0]:
                                agendado = True

                    if permitido:

                        preferencial = None
                        
                        if request.POST.get('preferencial') == '0':
                            preferencial = False
                        else:
                            preferencial = True                        

                        if preferencial:
                            ficha = Ficha()
                            ficha.numero = num2
                            ficha.preferencial = preferencial
                            ficha.usuario = usuario[0]
                            ficha.status = "AGUARDANDO"
                            ficha.save()
                            fila_preferencial.fichas.add(ficha)
                            
                            if agendado == False:
                                fila_preferencial.vagas -= 1
                                fila_normal.vagas -= 1
                            fila_preferencial.save()
                            fila_normal.save()

                        else:
                            ficha = Ficha()
                            ficha.numero = num1
                            ficha.preferencial = preferencial
                            ficha.usuario = usuario[0]
                            ficha.status = "AGUARDANDO"
                            ficha.save()
                            fila_normal.fichas.add(ficha)

                            if agendado == False:
                                fila_normal.vagas -= 1
                                fila_preferencial.vagas -= 1
                            fila_normal.save()
                            fila_preferencial.save()
                        fichas = []
                        fichas.append(ficha)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
                        tmpJson = serializers.serialize("json", fichas)
                        tmpObj = json.loads(tmpJson)  
                        return HttpResponse(json.dumps(tmpObj))
                    else:
                        return HttpResponse(status=status.HTTP_403_FORBIDDEN)
                else:
                    return HttpResponse(status=status.HTTP_403_FORBIDDEN)
            else:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        else:
            return HttpResponse(status=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED)

    @action(methods=['post'], detail=False)
    def cadastro_ficha_exame(self, request):
        exame = get_object_or_404(Exame, pk=request.POST.get('id_exame'))
        token = request.POST.get('token')
        token = token.replace('"', '')

        if token:
            user = User.objects.filter(auth_token=token)
            usuario = Usuario.objects.filter(user=user[0])
            permitido = True
            agendado = False
            fila_normal = None
            fila_preferencial = None
            num1 = 1
            num2 = 1
            if request.method == 'POST':
                if exame.create_fila:
                    
                    for fila in exame.filas.all():
                        if fila.fila_preferencial:
                            fila_preferencial = fila
                        else:
                            fila_normal = fila

                    for ficha in fila_normal.fichas.all():
                        if ficha.usuario == usuario[0]:
                            permitido = False
                        num1 = 1 + ficha.numero

                    for ficha in fila_preferencial.fichas.all():
                        if ficha.usuario == usuario[0]:
                            permitido = False
                        num2 = 1 + ficha.numero

                    if exame.agendamento and exame.agendamento.usuarios:
                        for user in exame.agendamento.usuarios.all():
                            if user == usuario[0]:
                                agendado = True

                    if permitido:

                        preferencial = None
                        
                        if request.POST.get('preferencial') == '0':
                            preferencial = False
                        else:
                            preferencial = True                        

                        if preferencial:
                            ficha = Ficha()
                            ficha.numero = num2
                            ficha.preferencial = preferencial
                            ficha.usuario = usuario[0]
                            ficha.status = "AGUARDANDO"
                            ficha.save()
                            fila_preferencial.fichas.add(ficha)
                            
                            if agendado == False:
                                fila_preferencial.vagas -= 1
                                fila_normal.vagas -= 1
                            fila_preferencial.save()
                            fila_normal.save()

                        else:
                            ficha = Ficha()
                            ficha.numero = num1
                            ficha.preferencial = preferencial
                            ficha.usuario = usuario[0]
                            ficha.status = "AGUARDANDO"
                            ficha.save()
                            fila_normal.fichas.add(ficha)

                            if agendado == False:
                                fila_normal.vagas -= 1
                                fila_preferencial.vagas -= 1
                            fila_normal.save()
                            fila_preferencial.save()
                        fichas = []
                        fichas.append(ficha)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
                        tmpJson = serializers.serialize("json", fichas)
                        tmpObj = json.loads(tmpJson)  
                        return HttpResponse(json.dumps(tmpObj))
                    else:
                        return HttpResponse(status=status.HTTP_403_FORBIDDEN)
                else:
                    return HttpResponse(status=status.HTTP_403_FORBIDDEN)
            else:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        else:
            return HttpResponse(status=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED)

    @action(methods=['post'], detail=False)
    def desistir_ficha(self, request):
        token = request.POST.get('token')
        token = token.replace('"', '')
        
        if token:
            ficha = get_object_or_404(Ficha, pk=request.POST.get('id_ficha'))
            user = User.objects.filter(auth_token=token)
            usuario = Usuario.objects.filter(user=user[0])
            filas = Fila.objects.filter(fichas=ficha)

            if request.method == 'POST':

                if ficha.usuario == usuario[0]:
                    ficha.delete()

                    for fila in filas.all():
                        fila.vagas += 1
                        fila.save()

                    return HttpResponse(status=status.HTTP_200_OK)
                else:
                    return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
            else:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        else:
            return HttpResponse(status=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED)

        
# --------------------------FIM API--------------------------------------

@login_required(login_url='/accounts/login')
def printPDF(request):
    if has_permission(request.user, 'permissao_usuario'):
        html_string = render_to_string('printPDF.html', {'context': contexto.get()})
        html = HTML(string=html_string)
        html.write_pdf(target='/tmp/ficha.pdf')
        fs = FileSystemStorage('/tmp')

        with fs.open('ficha.pdf') as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="ficha.pdf'
        return response
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home.html', {'context': context})

@login_required(login_url='/accounts/login')
def cadastroFichaConsulta(request, id):
    if has_permission(request.user, 'permissao_usuario'):
        consulta = get_object_or_404(Consulta, pk=id)
        usuario = Usuario.objects.filter(user=request.user)
        form = FormFicha(request.POST or None, request.FILES or None)
        permitido = True
        agendado = False
        fila_normal = None
        fila_preferencial = None
        num1 = 1
        num2 = 1
        if form.is_valid():
            if consulta.create_fila:
                
                for fila in consulta.filas.all():
                    if fila.fila_preferencial:
                        fila_preferencial = fila
                    else:
                        fila_normal = fila

                for ficha in fila_normal.fichas.all():
                    if ficha.usuario == usuario[0]:
                        permitido = False
                    num1 = 1 + ficha.numero

                for ficha in fila_preferencial.fichas.all():
                    if ficha.usuario == usuario[0]:
                        permitido = False
                    num2 = 1 + ficha.numero

                if consulta.agendamento.usuarios.all():
                    for user in consulta.agendamento.usuarios.all():
                        if user == usuario[0]:
                            agendado = True

            if permitido:

                preferencial = form.cleaned_data['preferencial']

                if preferencial:
                    ficha = Ficha()
                    ficha.numero = num2
                    ficha.preferencial = preferencial
                    ficha.usuario = usuario[0]
                    ficha.status = "AGUARDANDO"
                    ficha.save()
                    fila_preferencial.fichas.add(ficha)
                    
                    if agendado == False:
                        fila_preferencial.vagas -= 1
                        fila_normal.vagas -= 1
                    fila_preferencial.save()
                    fila_normal.save()

                else:
                    ficha = Ficha()
                    ficha.numero = num1
                    ficha.preferencial = preferencial
                    ficha.usuario = usuario[0]
                    ficha.status = "AGUARDANDO"
                    ficha.save()
                    fila_normal.fichas.add(ficha)

                    if agendado == False:
                        fila_normal.vagas -= 1
                        fila_preferencial.vagas -= 1
                    fila_normal.save()
                    fila_preferencial.save()

                return redirect('detalhesFicha', id=ficha.id)

            else:
                context = {
                    'msg_error': 'Você já está participando dessa fila!'
                }
                return render(request, 'home_usuario.html', {'context': context})

        return render(request, 'cadastro_ficha.html', {'form': form})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home.html', {'context': context})    


@login_required(login_url='/accounts/login')
def cadastroFichaAutorizacao(request, id):
    if has_permission(request.user, 'permissao_usuario'):
        print('aqui_2')
        autorizacao = get_object_or_404(Autorizacao, pk=id)
        usuario = Usuario.objects.filter(user=request.user) 
        form = FormFicha(request.POST or None, request.FILES or None)
        permitido = True
        agendado = False
        num1 = 1
        num2 = 1

        if form.is_valid():
            if autorizacao.create_fila:

                for fila in autorizacao.filas.all():
                    if fila.fila_preferencial:
                        fila_preferencial = fila
                    else:
                        fila_normal = fila

                for ficha in fila_normal.fichas.all():
                    if ficha.usuario == usuario[0]:
                        permitido = False
                    num1 = 1 + ficha.numero

                for ficha in fila_preferencial.fichas.all():
                    if ficha.usuario == usuario[0]:
                        permitido = False
                    num2 = 1 + ficha.numero
                
                if autorizacao.agendamento:
                    for user in autorizacao.agendamento.usuarios.all():
                        if user == usuario[0]:
                            agendado = True

            if permitido:
                preferencial = form.cleaned_data['preferencial']

                if preferencial:
                    ficha = Ficha()
                    ficha.numero = num2
                    ficha.preferencial = preferencial
                    ficha.usuario = usuario[0]
                    ficha.status = "AGUARDANDO"
                    ficha.save()
                    fila_preferencial.fichas.add(ficha)

                    if agendado == False:
                        fila_preferencial.vagas -= 1
                        fila_normal.vagas -= 1
                    
                    fila_preferencial.save()
                    fila_normal.save()

                else:
                    ficha = Ficha()
                    ficha.numero = num1
                    ficha.preferencial = preferencial
                    ficha.usuario = usuario[0]
                    ficha.status = "AGUARDANDO"
                    ficha.save()
                    fila_normal.fichas.add(ficha)

                    if agendado == False:
                        fila_preferencial.vagas -= 1
                        fila_normal.vagas -= 1

                    fila_normal.save()
                    fila_preferencial.save()

                return redirect('detalhesFicha', id=ficha.id)

            else:
                context = {
                    'msg_error': 'Você já está participando dessa fila!'
                }
                return render(request, 'home_usuario.html', {'context': context})

        return render(request, 'cadastro_ficha.html', {'form': form})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home.html', {'context': context})


@login_required(login_url='/accounts/login')
def cadastroFichaExame(request, id):
    if has_permission(request.user, 'permissao_usuario'):
        exame = get_object_or_404(Exame, pk=id)
        usuario = Usuario.objects.filter(user=request.user) 
        form = FormFicha(request.POST or None, request.FILES or None)
        permitido = True
        agendado = False
        num1 = 1
        num2 = 1

        if form.is_valid():
            if exame.create_fila:

                for fila in exame.filas.all():
                    if fila.fila_preferencial:
                        fila_preferencial = fila
                    else:
                        fila_normal = fila

                for ficha in fila_normal.fichas.all():
                    if ficha.usuario == usuario[0]:
                        permitido = False
                    num1 = 1 + ficha.numero

                for ficha in fila_preferencial.fichas.all():
                    if ficha.usuario == usuario[0]:
                        permitido = False
                    num2 = 1 + ficha.numero
                
                if exame.agendamento:
                    for user in exame.agendamento.usuarios.all():
                        if user == usuario[0]:
                            agendado = True

            if permitido:
                preferencial = form.cleaned_data['preferencial']

                if preferencial:
                    ficha = Ficha()
                    ficha.numero = num2
                    ficha.preferencial = preferencial
                    ficha.usuario = usuario[0]
                    ficha.status = "AGUARDANDO"
                    ficha.save()
                    fila_preferencial.fichas.add(ficha)

                    if agendado == False:
                        fila_preferencial.vagas -= 1
                        fila_normal.vagas -= 1
                    
                    fila_preferencial.save()
                    fila_normal.save()

                else:
                    ficha = Ficha()
                    ficha.numero = num1
                    ficha.preferencial = preferencial
                    ficha.usuario = usuario[0]
                    ficha.status = "AGUARDANDO"
                    ficha.save()
                    fila_normal.fichas.add(ficha)

                    if agendado == False:
                        fila_preferencial.vagas -= 1
                        fila_normal.vagas -= 1

                    fila_normal.save()
                    fila_preferencial.save()

                return redirect('detalhesFicha', id=ficha.id)

            else:
                context = {
                    'msg_error': 'Você já está participando dessa fila!'
                }
                return render(request, 'home_usuario.html', {'context': context})

        return render(request, 'cadastro_ficha.html', {'form': form})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home.html', {'context': context})

@login_required(login_url='/accounts/login')
def cadastroFichaAgendamento(request, id):
    if has_permission(request.user, 'permissao_usuario'):
        agendamento = get_object_or_404(Agendamento, pk=id)
        form = FormFicha(request.POST or None, request.FILES or None)
        consulta = Consulta.objects.filter(agendamento=agendamento)
        exame = Exame.objects.filter(agendamento=agendamento)
        autorizacao = Autorizacao.objects.filter(agendamento=agendamento)

        if consulta:
            return redirect('cadastroFichaConsulta', id=consulta[0].id)
        elif autorizacao:
            return redirect('cadastroFichaAutorizacao', id=autorizacao[0].id)
        elif exame:
            return redirect('cadastroFichaExame', id=exame[0].id)
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home.html', {'context': context})    

@login_required(login_url='/accounts/login')
def deleteFicha(request, id):
    if has_permission(request.user, 'permissao_usuario'):
        ficha = get_object_or_404(Ficha, pk=id)
        usuario = Usuario.objects.filter(user=request.user)
        filas = Fila.objects.filter(fichas=ficha)

        if request.method == 'POST':

            if ficha.usuario == usuario[0]:
                ficha.delete()

                for fila in filas.all():
                    fila.vagas += 1
                    fila.save()

                context = {
                    'msg_alert_success': 'Exclusão realizada com sucesso'
                }

            else:
                context = {
                    'msg_alert_error': 'Você não participa dessa fila'
                }

            return render(request, 'home_usuario.html', {'context': context})

        return render(request, 'delete_ficha.html', {'ficha': ficha})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home.html', {'context': context})


@login_required(login_url='/accounts/login')
def detalhesFicha(request, id):
    if has_permission(request.user, 'permissao_usuario'):
        ficha = get_object_or_404(Ficha, pk=id)
        filas = Fila.objects.filter(fichas=ficha)
        usuario = ficha.usuario
        fila_preferencial = None
        fila_normal = None
        unidade_aux = None

        for fila in filas.all():
            if fila.fila_preferencial:
                fila_preferencial = fila
            else:
                fila_normal = fila

        if fila_preferencial:

            consulta = Consulta.objects.filter(filas=fila_preferencial)
            autorizacao = Autorizacao.objects.filter(filas=fila_preferencial)

            if consulta:
                unidade = UnidadeSaude.objects.filter(consultas=consulta[0])
                unidade_aux = unidade[0]


            elif autorizacao:
                unidade = UnidadeSaude.objects.filter(autorizacoes=autorizacao[0])
                unidade_aux = unidade[0]

            context = {
                'ficha': ficha,
                'fila_preferencial': fila_preferencial,
                'usuario': usuario,
                'unidade': unidade_aux
            }
        else:
            consulta = Consulta.objects.filter(filas=fila_normal)
            autorizacao = Autorizacao.objects.filter(filas=fila_normal)

            if consulta:
                unidade = UnidadeSaude.objects.filter(consultas=consulta[0])
                unidade_aux = unidade[0]

            elif autorizacao:
                unidade = UnidadeSaude.objects.filter(autorizacoes=autorizacao[0])
                unidade_aux = unidade[0]

            context = {
                'ficha': ficha,
                'fila_normal': fila_normal,
                'usuario': usuario,
                'unidade': unidade_aux
            }
        contexto.set(context)

        return render(request, 'detalhes_ficha.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home.html', {'context': context})

class Context(object):
    def __init__(self, context):
        self.__context = context
    
    def get(self):
        return self.__context

    def set(self, context):
        self.__context = context

contexto = Context(None)



