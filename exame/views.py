from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import FormExame
from ficha.models import Ficha
from fila.models import Fila
from .models import Exame
from unidadeSaude.models import UnidadeSaude
from datetime import date
from rolepermissions.checkers import has_permission
from rest_framework.decorators import action
from rest_framework.response import Response
import json
from django.core import serializers
from rest_framework.filters import SearchFilter
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from rest_framework import viewsets
from exame.serializers import ExameSerializer
from rest_framework import status

class GetExameViewSet(viewsets.ModelViewSet):
    serializer_class = ExameSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('^nome', '^data', '^status', '^tipo')

    def get_queryset(self):
        queryset = Exame.objects.all()
        return queryset

    @action(methods=['get'], detail=True)
    def exame_ficha(self, request, pk=None):
        ficha = get_object_or_404(Ficha, pk=pk)
        filas = Fila.objects.filter(fichas=ficha)
        exame = Exame.objects.filter(filas=filas[0])
        tmpJson = serializers.serialize("json", exame)
        tmpObj = json.loads(tmpJson)
        return HttpResponse(json.dumps(tmpObj))
    
    @action(methods=['get'], detail=True)
    def get_status_exame(self, request, pk=None):
        exame = get_object_or_404(Exame, pk=pk)

        if exame.status == 'INICIADA':
            return HttpResponse(status=status.HTTP_200_OK)
        else:
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)


@login_required(login_url='/accounts/login')
def cadastroExame(request):
    if has_permission(request.user, 'permissao_unidade'):
        form = FormExame(request.POST or None, request.FILES or None)

        if form.is_valid():
            exame = Exame(tipo=form.cleaned_data['tipo'], nome=form.cleaned_data['nome'], data=form.cleaned_data['data'], hora=request.POST.get('hora'))
            exame.user = request.user
            exame.create_fila = False
            exame.status = "AGUARDANDO"
            exame.save()
            unidade = UnidadeSaude.objects.filter(users=request.user)
            if unidade:
                unidade[0].exames.add(exame)
                unidade[0].save()
            
            return redirect('listaExame')
        
        return render(request, 'cadastro_exame.html', {'form': form})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})

@login_required(login_url='/accounts/login')
def listaExame(request):
    if has_permission(request.user, 'permissao_unidade'):
        unidade = UnidadeSaude.objects.filter(users=request.user)
        pesquisa = request.GET.get('pesquisa', None)
        data = request.GET.get('data', None)

        if unidade:
            exames = unidade[0].exames.all().order_by('data', 'hora', '-create_fila')
            
            if pesquisa:

                exames = exames.filter(nome__icontains=pesquisa) | exames.filter(status__icontains=pesquisa) | exames.filter(tipo__icontains=pesquisa)
                
                if exames:
                    context = {
                        'exames': exames
                    }
                else:
                    exames = unidade[0].exames.all().order_by('data', 'hora', '-create_fila')
                    context = {
                        'exames': exames,
                        'msg_busca': 'Nada encontrado para esses parâmetros!'
                    }        
            elif data:
                exames = exames.filter(data=data).order_by('data', 'hora', '-create_fila')
                
                if exames:
                    context = {
                        'exames': exames
                    }
                
                else:
                    exames = unidade[0].exames.all().order_by('data', 'hora', '-create_fila')
                    context = {
                        'exames': exames,
                        'msg_busca': 'Nada encontrado para esses parâmetros!'
                    }
        
            elif exames:
                context = {
                    'exames': exames
                }

            else:
                context = {
                    'msg_alert': 'Nenhum Exame Cadastrado!'
                }
                
            contexto.set(context)
            
            return render(request, 'lista_exame.html', {'context': context})

        else:
            context = {
                'msg_error': 'Indisponivel Acessar Essa Área'
            }

            return render(request, 'home.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})

@login_required(login_url='/accounts/login')
def alterarExame(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        exame = get_object_or_404(Exame, pk=id)
        form = FormExame(request.POST or None, request.FILES or None, instance=exame)
        fila_normal = None
        fila_preferencial = None

        if exame.filas.all():
            for fila in consulta.filas.all():
                if fila.fila_preferencial:
                    fila_preferencial = fila
                else:
                    fila_normal = fila

        if exame.user == request.user:
            if form.is_valid():
                exame.hora = request.POST.get('hora')
                form.save()
                exame.save()

                #NOTIFICAÇÂO
                mensagem = 'Atenção, o exame: '+ exame.nome + 'teve uma alteração, fique atento!'

                if fila_normal:
                    if fila_normal.fichas.all():
                        notificacoes.notificacaoColetiva(request, mensagem, fila_normal.fichas.all())
                
                if fila_preferencial:
                    if fila_preferencial.fichas.all():
                        notificacoes.notificacaoColetiva(request, mensagem, fila_preferencial.fichas.all())
                
                if exame.agendamento:
                    if exame.agendamento.usuarios.all():
                        notificacoes.notificacaoAgendamento(request, mensagem, exame.agendamento)
                
                return redirect('listaExame')

        elif exame.user != request.user:
            context = {
                'msg_error': 'Indisponivel Acessar Essa Área'

            }
            return redirect('homeUnidadeSaude', {'context': context})

        context = {
            'form': form,
            'exame': exame,
        }

        return render(request, 'cadastro_exame.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})


@login_required(login_url='/accounts/login')
def deleteExame(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        exame = get_object_or_404(Exame, pk=id)
        fila_normal = None
        fila_preferencial = None
        agendamento = exame.agendamento

        for fila in exame.filas.all():
            if fila.fila_preferencial:
                fila_preferencial = fila
            else:
                fila_normal = fila

        if exame.user == request.user:
            if request.method == 'POST':
                
                if fila_normal != None:
                    fila_normal.delete()
                    fila_preferencial.delete()
                
                if agendamento != None:
                    agendamento.delete()

                exame.delete()
                return redirect('listaExame')
        elif exame.user != request.user:
            context = {
                'msg_error': 'Indisponivel Acessar Essa Área'

            }
            return redirect('homeUnidadeSaude', {'context': context})

        return render(request, 'delete_exame.html', {'nome': exame.nome})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})

@login_required(login_url='/accounts/login')
def detalhesExame(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        exame = get_object_or_404(Exame, pk=id)
        fila_normal = None
        fila_preferencial = None
        fichas_normais = [None]
        fichas_preferenciais = [None]

        for fila in exame.filas.all():
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
            'exame': exame,
            'fila_preferencial': fila_preferencial,
            'fila_normal': fila_normal,
            'fichas_normais': fichas_normais,
            'fichas_preferenciais': fichas_preferenciais
        }

        contexto.set(context)

        return render(request, 'detalhes_exame.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})

@login_required(login_url='/accounts/login')
def iniciarExame(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        exame = get_object_or_404(Exame, pk=id)
        fila_normal = None
        fila_preferencial = None

        if exame.filas.all():
            for fila in exame.filas.all():
                if fila.fila_preferencial:
                    fila_preferencial = fila
                else:
                    fila_normal = fila
            
            exame.status = "INICIADA"
            exame.save()

            if exame.filas.all():
                if fila_normal.fichas.all() or fila_preferencial.fichas.all():
                    #PARTE DO ENVIO DA NOTIFICACAO
                    mensagem = "O exame: " + exame.nome + " foi iniciado, fique atento para não perder a sua vez!"
                    notificacoes.inicioConsultaAutorizacao(request, mensagem, exame)

            context = {
                'exame': exame,
                'fila_preferencial': fila_preferencial,
                'fila_normal': fila_normal
            }

            return render(request, 'detalhes_exame.html', {'context': context})
        else:
            context = {
                'exame': exame,
                'msg_error': 'Exame sem fila'
            }
            return render(request, 'detalhes_exame.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})

@login_required(login_url='/accounts/login')
def encerrarExame(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        exame = get_object_or_404(Exame, pk=id)
        fila_normal = None
        fila_preferencial = None

        if request.method == 'POST':
            exame.status = 'ENCERRADA'
            exame.save()
            
            for fila in exame.filas.all():
                if fila.fila_preferencial:
                    fila_preferencial = fila
                else:
                    fila_normal = fila

            context = {
                'exame': exame,
                'fila_preferencial': fila_preferencial,
                'fila_normal': fila_normal
            }

            return render(request, 'detalhes_exame.html', {'context': context})
        
        return render(request, 'encerrar_exame.html', {'exame': exame})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})

@login_required(login_url='/accounts/login')
def listaExameUsuario(request):
    if has_permission(request.user, 'permissao_usuario'):
        exames = Exame.objects.all().order_by('hora', '-data', '-create_fila')
        pesquisa = request.GET.get('pesquisa', None)
        data = request.GET.get('data', None)

        if data:
            exames = exames.filter(data=data).order_by('hora', '-data', '-create_fila')
            if exames:
                context = {
                    'exames': exames
                }
            else:
                exames = exames.objects.all().order_by('hora', '-data', '-create_fila')
                context = {
                    'exames': exames,
                    'msg_busca': 'Nada encontrado para esses parâmetros!'
                }
        elif pesquisa:
            exames = exames.filter(nome__icontains=pesquisa).order_by('hora', '-data', '-create_fila') | exames.filter(status__icontains=pesquisa).order_by('hora', '-data', '-create_fila') | exames.filter(tipo__icontains=pesquisa).order_by('hora', '-data', '-create_fila')
            if exames:
                context = {
                    'exames': exames
                }
            else:
                exames = exames.objects.all().order_by('hora', '-data', '-create_fila')
                context = {
                    'exames': exames,
                    'msg_busca': 'Nada encontrado para esses parâmetros!'
                }
        elif exames:
            context = {
                'exames': exames
            }
        else:
            context = {
                'msg_error': 'Nenhuma autorização cadastrada!'
            }

        return render(request, 'lista_exame_usuario.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home.html', {'context': context})

@login_required(login_url='/accounts/login')
def detalhesExameUsuario(request, id):
    if has_permission(request.user, 'permissao_usuario'):
        exame = get_object_or_404(Exame, pk=id)
        unidade = UnidadeSaude.objects.filter(exames=exame)

        context = {
            'exame': exame,
            'unidade': unidade[0]
        }

        return render(request, 'detalhes_exame_usuario.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home.html', {'context': context})


@login_required(login_url='/accounts/login')
def listaExamesAguardando(request):
    if has_permission(request.user, 'permissao_unidade'):
        hoje = date.today()
        unidade = UnidadeSaude.objects.filter(users=request.user)
        exames = unidade[0].exames.filter(status='AGUARDANDO', data=hoje)

        if exames:
            context = {
                'exames': exames
            }
        else:
            context = {
                'msg_error': 'Nenhum exame aguardando para a data de hoje!'
            }

        return render(request, 'lista_exames_aguardando.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})

@login_required(login_url='/accounts/login')
def relatorioListaExame(request):
    if has_permission(request.user, 'permissao_unidade'):
        html_string = render_to_string('relatorio_lista_exame.html', {'context': contexto.get()})
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        html.write_pdf(target='/tmp/relatorio_lista_exame.pdf', presentational_hints=True)
        fs = FileSystemStorage('/tmp')

        with fs.open('relatorio_lista_exame.pdf') as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="relatorio_lista_exame.pdf'
        return response
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home.html', {'context': context})

@login_required(login_url='/accounts/login')
def relatorioExame(request):
    if has_permission(request.user, 'permissao_unidade'):
        html_string = render_to_string('relatorio_exame.html', {'context': contexto.get()})
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        html.write_pdf(target='/tmp/relatorio_autorizacao.pdf', presentational_hints=True)
        fs = FileSystemStorage('/tmp')

        with fs.open('relatorio_autorizacao.pdf') as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="relatorio_autorizacao.pdf'
        return response
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


