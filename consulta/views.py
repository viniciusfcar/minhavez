from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Consulta
from .forms import FormConsulta
from usuario.models import Usuario
from django.contrib.auth.models import User
from ficha.models import Ficha
from fila.models import Fila
from unidadeSaude.models import UnidadeSaude
from rest_framework import viewsets
from .serializers import ConsultaSerializer
from datetime import date
from autorizacao.models import Autorizacao
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration
from especialista.models import Especialista
from rolepermissions.checkers import has_permission
from rest_framework.decorators import action
from rest_framework.response import Response
import json
from django.core import serializers
from rest_framework.filters import SearchFilter
from notificacoes import views as notificacoes
from rest_framework import status

class GetConsultaViewSet(viewsets.ModelViewSet):
    serializer_class = ConsultaSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('^nome', '^data', '^status', '^especialista__nome', '^especialista__profissao__nome', '^especialista__especializacao__nome')

    def get_queryset(self):
        queryset = Consulta.objects.all()
        return queryset

    @action(methods=['get'], detail=True)
    def consulta_ficha(self, request, pk=None):
        ficha = get_object_or_404(Ficha, pk=pk)
        filas = Fila.objects.filter(fichas=ficha)
        consulta = Consulta.objects.filter(filas=filas[0])
        tmpJson = serializers.serialize("json", consulta)
        tmpObj = json.loads(tmpJson)
        return HttpResponse(json.dumps(tmpObj))

    @action(methods=['get'], detail=True)
    def get_status_consulta(self, request, pk=None):
        consulta = get_object_or_404(Consulta, pk=pk)

        if consulta.status == 'INICIADA':
            return HttpResponse(status=status.HTTP_200_OK)
        else:
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)


@login_required(login_url='/accounts/login')
def cadastroConsulta(request):
    if has_permission(request.user, 'permissao_unidade'):
        if request.method == 'POST':

            form = FormConsulta(request.POST or None, request.FILES or None)
            
            if form.is_valid():
                consulta = Consulta(nome=form.cleaned_data['nome'], data=form.cleaned_data['data'], hora=request.POST.get('hora'))
                especialista = form.cleaned_data['especialista']
                consulta.especialista = especialista
                consulta.user = request.user
                consulta.create_fila = False
                consulta.status = "AGUARDANDO"
                consulta.save()
                unidade = UnidadeSaude.objects.filter(users=request.user)
                if unidade:
                    unidade[0].consultas.add(consulta)
                    unidade[0].save()

                return redirect('listaConsulta')
        else:
            form = FormConsulta()

        return render(request, 'cadastro_consulta.html', {'form': form})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})


@login_required(login_url='/accounts/login')
def listaConsulta(request):
    if has_permission(request.user, 'permissao_unidade'):
        unidade = UnidadeSaude.objects.filter(users=request.user)
        pesquisa = request.GET.get('pesquisa', None)
        data = request.GET.get('data', None)

        if unidade:
            consultas = unidade[0].consultas.all().order_by('data', 'hora', '-create_fila')

            if pesquisa:
                espe = Especialista.objects.filter(nome__icontains=pesquisa)

                if espe:
                    consultas = consultas.filter(nome__icontains=pesquisa) | consultas.filter(status__icontains=pesquisa) | consultas.filter(especialista__name__icontains=espe[0])

                    if consultas:
                        context = {
                            'consultas': consultas
                        }
                    else:
                        consultas = unidade[0].consultas.all().order_by('data', 'hora', '-create_fila')
                        context = {
                            'consultas': consultas,
                            'msg_busca': 'Nada encontrado para esses parâmetros!'
                        }
                else:
                    consultas = consultas.filter(nome__icontains=pesquisa) | consultas.filter(status__icontains=pesquisa)
                    if consultas:
                        context = {
                            'consultas': consultas
                        }
                    else:
                        consultas = unidade[0].consultas.all().order_by('data', 'hora', '-create_fila')
                        
                        context = {
                            'msg_busca': 'Nada encontrado para esses parâmetros!'
                        }        
            elif data:
                consultas = consultas.filter(data=data)
                if consultas:
                    context = {
                        'consultas': consultas
                    }
                
                else:
                    consultas = unidade[0].consultas.all().order_by('data', 'hora', '-create_fila')
                    context = {
                        'consultas': consultas,
                        'msg_busca': 'Nada encontrado para esses parâmetros!'
                    }
        
            elif consultas:
                context = {
                    'consultas': consultas
                }

            else:
                context = {
                    'msg_alert': 'Nenhuma Consulta Cadastrada!'
                }

            contexto.set(context)
            
            return render(request, 'lista_consulta.html', {'context': context})

        else:
            context = {
                'msg_error': 'Indisponivel Acessar Essa Área'

            }

        return render(request, 'home_unidade_saude.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})


@login_required(login_url='/accounts/login')
def alterarConsulta(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        consulta = get_object_or_404(Consulta, pk=id)
        form = FormConsulta(request.POST or None, request.FILES or None, instance=consulta)
        fila_normal = None
        fila_preferencial = None

        if consulta.filas.all():
            for fila in consulta.filas.all():
                if fila.fila_preferencial:
                    fila_preferencial = fila
                else:
                    fila_normal = fila

        if consulta.user == request.user:
            if form.is_valid():                
                consulta.hora = request.POST.get('hora')
                form.save()
                consulta.save()

                #NOTIFICAÇÂO
                mensagem = 'Atenção, a consulta: '+ consulta.nome + 'teve uma alteração, fique atento!'

                if fila_normal:
                    if fila_normal.fichas.all():
                        notificacoes.notificacaoColetiva(request, mensagem, fila_normal.fichas.all())
                
                if fila_preferencial:
                    if fila_preferencial.fichas.all():
                        notificacoes.notificacaoColetiva(request, mensagem, fila_preferencial.fichas.all())
                
                if consulta.agendamento:
                    if consulta.agendamento.usuarios.all():
                        notificacoes.notificacaoAgendamento(request, mensagem, consulta.agendamento)
                
                return redirect('listaConsulta')
        else:
            context = {
                'msg_error': 'Indisponivel Acessar Essa Área'

            }
            return redirect('homeUnidadeSaude', {'context': context})

        return render(request, 'cadastro_consulta.html', {'form': form})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})


@login_required(login_url='/accounts/login')
def deleteConsulta(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        consulta = get_object_or_404(Consulta, pk=id)
        fila_normal = None
        fila_preferencial = None
        agendamento = consulta.agendamento

        for fila in consulta.filas.all():
            if fila.fila_preferencial:
                fila_preferencial = fila
            else:
                fila_normal = fila

        if consulta.user == request.user:
            if request.method == 'POST':
                if fila_normal != None:
                    fila_normal.delete()
                    fila_preferencial.delete()
                
                if agendamento != None:
                    agendamento.delete()
                    
                consulta.delete()
                return redirect('listaConsulta')
        else:
            context = {
                'msg_error': 'Indisponivel Acessar Essa Área'

            }
            return redirect('homeUnidadeSaude', {'context': context})

        return render(request, 'delete_consulta.html', {'nome': consulta.nome})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})

@login_required(login_url='/accounts/login')
def detalhesConsulta(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        consulta = get_object_or_404(Consulta, pk=id)
        fila_normal = None
        fila_preferencial = None
        fichas_normais = [None]
        fichas_preferenciais = [None]

        for fila in consulta.filas.all():
            if fila.fila_preferencial:
                fila_preferencial = fila
            else:
                fila_normal = fila

        if fila_normal:
            for ficha in fila_normal.fichas.all():
                fichas_normais.append(ficha)

        if fila_preferencial:
            for ficha in fila_preferencial.fichas.all():
                fichas_preferenciais.append(ficha)

        context = {
            'consulta': consulta,
            'fila_preferencial': fila_preferencial,
            'fila_normal': fila_normal,
            'fichas_normais': fichas_normais,
            'fichas_preferenciais': fichas_preferenciais
        }

        contexto.set(context)
        return render(request, 'detalhes_consulta.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})

#METODOS QUE POSSIVELMENTE NÃO ESTOU MAIS USANDO
'''
@login_required(login_url='/accounts/login')
def adicionaUsuarioConsulta(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        consulta = get_object_or_404(Consulta, pk=id)
        usuario = Usuario.objects.filter(user=request.user)

        if consulta.vagas > 0:
            consulta.usuarios.append(usuario)
        if consulta.user == request.user:
            if usuario:
                consulta.usuarios.add(usuario[0])
                context = {
                    'consulta': consulta,
                    'usuarios': consulta.usuarios
                }
            else:
                usuarios = consulta.usuarios
                context = {
                    'consulta': consulta,
                    'usuarios': usuarios
                }
                print('CPF não localizado')
        else:
            context = {
                'msg_error': 'Indisponivel Acessar Essa Área'

            }
            return redirect('homeUnidadeSaude', {'context': context})

        return render(request, 'detalhes_consulta.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})


@login_required(login_url='/accounts/login')
def excluiUsuarioConsulta(request, cpf, id):
    if has_permission(request.user, 'permissao_unidade'):
        consulta = get_object_or_404(Consulta, pk=id)
        usuario = Usuario.objects.filter(cpf=cpf)

        if consulta.user == request.user:
            context = {
                'consulta': consulta,
                'usuarios': consulta.usuarios,
                'usuario': usuario[0],
            }

            if request.method == 'POST':
                consulta.usuarios.remove(usuario[0])
                return redirect('detalhesAtendimento', id=consulta.id)

        else:
            context = {
                'msg_error': 'Indisponivel Acessar Essa Área'

            }
            return redirect('homeUnidadeSaude', {'context': context})

        return render(request, 'exclui_usuario_consulta.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})
'''

@login_required(login_url='/accounts/login')
def listaConsultaUsuario(request):
    if has_permission(request.user, 'permissao_usuario'):
        consultas = Consulta.objects.all().order_by('-data', '-create_fila')
        pesquisa = request.GET.get('pesquisa', None)
        espe = Especialista.objects.filter(nome=request.GET.get('pesquisa', None))
        data = request.GET.get('data', None)

        if espe:
            consultas = consultas.filter(especialista__icontains=espe[0]) | consultas.filter(nome__icontains=pesquisa) | consultas.filter(status__icontains=pesquisa)

            if consultas:
                context = {
                    'consultas': consultas
                }
            else:
                consultas = Consulta.objects.all().order_by('-hora', '-data', '-create_fila')
                context = {
                    'consultas': consultas,
                    'msg_busca': 'Nada encontrado para esses parâmetros!'
                }
        elif data:
            consultas = consultas.filter(data=data).order_by('-hora', '-data', '-create_fila')

            if consultas:
                context = {
                    'consultas': consultas
                }
            else:
                consultas = Consulta.objects.all().order_by('-hora', '-data', '-create_fila')
                context = {
                    'consultas': consultas,
                    'msg_busca': 'Nada encontrado para esses parâmetros!'
                }
        elif pesquisa:
            consultas = consultas.filter(nome__icontains=pesquisa) | consultas.filter(status__icontains=pesquisa)

            if consultas:
                context = {
                    'consultas': consultas
                }
            else:
                consultas = Consulta.objects.all().order_by('-hora', '-data', '-create_fila')
                context = {
                    'consultas': consultas,
                    'msg_busca': 'Nada encontrado para esses parâmetros!'
                }
        elif consultas:
            context = {
                'consultas': consultas
            }
        else:
            context = {
                'msg_error': 'Nenhuma consulta cadastrada!'
            }
        
        return render(request, 'lista_consulta_usuario.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home.html', {'context': context})


@login_required(login_url='/accounts/login')
def detalhesConsultaUsuario(request, id):
    if has_permission(request.user, 'permissao_usuario'):
        consulta = get_object_or_404(Consulta, pk=id)
        unidade = UnidadeSaude.objects.filter(consultas=consulta)

        context = {
            'consulta': consulta,
            'unidade': unidade[0]
        }

        return render(request, 'detalhes_consulta_usuario.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home.html', {'context': context})

@login_required(login_url='/accounts/login')
def iniciarConsulta(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        consulta = get_object_or_404(Consulta, pk=id)
        fila_normal = None
        fila_preferencial = None

        if consulta.filas.all():
            for fila in consulta.filas.all():
                if fila.fila_preferencial:
                    fila_preferencial = fila
                else:
                    fila_normal = fila

            consulta.status = "INICIADA"
            consulta.save()
            
            if consulta.filas.all():
                if fila_normal.fichas.all() or fila_preferencial.fichas.all():
                    #PARTE DO ENVIO DA NOTIFICACAO
                    mensagem = "A consulta: " + consulta.nome + " foi iniciada, fique atento para não perder a sua vez!"
                    notificacoes.inicioConsultaAutorizacao(request, mensagem, consulta)

            context = {
                'consulta': consulta,
                'fila_preferencial': fila_preferencial,
                'fila_normal': fila_normal
            }

            return render(request, 'detalhes_consulta.html', {'context': context})
        else:
            context = {
                'consulta': consulta,
                'msg_error': 'Consulta sem fila!'
            }
            return render(request, 'detalhes_consulta.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})

@login_required(login_url='/accounts/login')
def encerrarConsulta(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        consulta = get_object_or_404(Consulta, pk=id)
        fila_normal = None
        fila_preferencial = None

        if request.method == 'POST':
            for fila in consulta.filas.all():
                if fila.fila_preferencial:
                    fila_preferencial = fila
                else:
                    fila_normal = fila
            
            consulta.status = "ENCERRADA"
            consulta.save()
            
            context = {
                'consulta': consulta,
                'fila_preferencial': fila_preferencial,
                'fila_normal': fila_normal
            }

            return render(request, 'detalhes_consulta.html', {'context': context})
        
        return render(request, 'encerrar_consulta.html', {'consulta': consulta})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})

@login_required(login_url='/accounts/login')
def listaConsultasAguardando(request):
    if has_permission(request.user, 'permissao_unidade'):
        hoje = date.today()
        unidade = UnidadeSaude.objects.filter(users=request.user)
        consultas = unidade[0].consultas.filter(status='AGUARDANDO', data=hoje)

        if consultas:
            context = {
                'consultas': consultas
            }
        else:
            context = {
                'msg_error': 'Nenhuma consulta aguardando para a data de hoje!'
            }
        
        return render(request, 'lista_consultas_aguardando.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context}) 

@login_required(login_url='/accounts/login')
def relatorioListaConsulta(request):
    if has_permission(request.user, 'permissao_unidade'):
        html_string = render_to_string('relatorio_lista_consulta.html', {'context': contexto.get()})
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        html.write_pdf(target='/tmp/relatorio_lista_consulta.pdf', presentational_hints=True)
        fs = FileSystemStorage('/tmp')

        with fs.open('relatorio_lista_consulta.pdf') as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="relatorio_lista_consulta.pdf'
        return response
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})

@login_required(login_url='/accounts/login')
def relatorioConsulta(request):
    if has_permission(request.user, 'permissao_unidade'):
        html_string = render_to_string('relatorio_consulta.html', {'context': contexto.get()})
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        html.write_pdf(target='/tmp/relatorio_consulta.pdf', presentational_hints=True)
        fs = FileSystemStorage('/tmp')

        with fs.open('relatorio_consulta.pdf') as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="relatorio_consulta.pdf'
        return response
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})

class Context(object):
    def __init__(self, context):
        self.__context = context
    
    def get(self):
        return self.__context

    def set(self, context):
        self.__context = context

contexto = Context(None)  

    
    
    