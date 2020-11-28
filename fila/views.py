from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Fila
from consulta.models import Consulta
from exame.models import Exame
from .forms import FormFila
from autorizacao.models import Autorizacao
from unidadeSaude.models import UnidadeSaude
from rest_framework import viewsets
from .serializers import FilaSerializer
from agendamento.models import Agendamento
from ficha.models import Ficha
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from rolepermissions.checkers import has_permission
from rest_framework.decorators import action
from rest_framework.response import Response
import json
from django.core import serializers
from notificacoes import views as notificacoes


class GetFilaViewSet(viewsets.ModelViewSet):
    serializer_class = FilaSerializer

    def get_queryset(self):
        queryset = Fila.objects.all()
        return queryset

    @action(methods=['get'], detail=True)
    def fila_ficha(self, request, pk=None):
        ficha = get_object_or_404(Ficha, pk=pk)
        filas = Fila.objects.filter(fichas=ficha)
        tmpJson = serializers.serialize("json", filas)
        tmpObj = json.loads(tmpJson)
        return HttpResponse(json.dumps(tmpObj))


@login_required(login_url='/accounts/login')
def cadastroFilaConsulta(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        consulta = get_object_or_404(Consulta, pk=id)
        form = FormFila(request.POST or None, request.FILES or None)

        if consulta.user == request.user:
            if form.is_valid():
                vagas = form.cleaned_data['vagas']
                
                if consulta.agendamento:
                    total_usuarios = consulta.agendamento.usuarios.count()
                    vagas -= total_usuarios

                fila_normal = Fila(nome=form.cleaned_data['nome'], vagas=vagas)
                fila_normal.fila_preferencial = False
                fila_preferencial = Fila(nome=form.cleaned_data['nome']+' Preferencial', vagas=vagas)
                fila_preferencial.fila_preferencial = True
                fila_normal.save()
                fila_preferencial.save()
                consulta.filas.add(fila_normal)
                consulta.filas.add(fila_preferencial)
                consulta.create_fila = True
                
                if consulta.verifica:
                    consulta.agendamento.participar = True
                    consulta.agendamento.save()
                
                consulta.save()
                
                if consulta.agendamento:
                    if consulta.agendamento.usuarios.all():
                        #NOTIFICAÇÂO
                        mensagem = 'Atenção, a consulta: '+ consulta.nome + ' iniciou suas filas, marque seu lugar na fila desejada!'
                        notificacoes.notificacaoAgendamento(request, mensagem, consulta.agendamento)

                return redirect('detalhesConsulta', id=consulta.id)
        else:
            context = {
                'msg_error': 'Indisponivel Acessar Essa Área'
            }

            return render(request, 'home_usuario.html', {'context': context})

        return render(request, 'cadastro_fila_consulta.html', {'form': form})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})


@login_required(login_url='/accounts/login')
def cadastroFilaAutorizacao(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        autorizacao = get_object_or_404(Autorizacao, pk=id)
        form = FormFila(request.POST or None, request.FILES or None)

        if autorizacao.user == request.user:
            if form.is_valid():
                fila = Fila(nome=form.cleaned_data['nome'], vagas=form.cleaned_data['vagas'])
                fila.fila_preferencial = False
                preferencial = Fila(nome=form.cleaned_data['nome']+' Preferencial', vagas=form.cleaned_data['vagas'])
                preferencial.fila_preferencial = True
                fila.save()
                preferencial.save()
                autorizacao.filas.add(fila)
                autorizacao.filas.add(preferencial)
                autorizacao.create_fila = True

                #Faz com que o úsuario possa participar da fila pelo agendamento
                if autorizacao.verifica:
                    autorizacao.agendamento.participar = True
                    autorizacao.agendamento.save()
                autorizacao.save()

                if autorizacao.agendamento:
                    if autorizacao.agendamento.usuarios.all():
                        #NOTIFICAÇÂO
                        mensagem = 'Atenção, a autorização: '+ autorizacao.nome + ' iniciou suas filas, marque seu lugar na fila desejada!'
                        notificacoes.notificacaoAgendamento(request, mensagem, autorizacao.agendamento)

                return redirect('detalhesAutorizacao', id=autorizacao.id)
        else:
            context = {
                'msg_error': 'Indisponivel Acessar Essa Área'
            }

            return render(request, 'home_unidade_saude.html', {'context': context})

        return render(request, 'cadastro_fila_autorizacao.html', {'form': form})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})


@login_required(login_url='/accounts/login')
def cadastroFilaExame(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        exame = get_object_or_404(Exame, pk=id)
        form = FormFila(request.POST or None, request.FILES or None)

        if exame.user == request.user:
            if form.is_valid():
                fila = Fila(nome=form.cleaned_data['nome'], vagas=form.cleaned_data['vagas'])
                fila.fila_preferencial = False
                preferencial = Fila(nome=form.cleaned_data['nome']+' Preferencial', vagas=form.cleaned_data['vagas'])
                preferencial.fila_preferencial = True
                fila.save()
                preferencial.save()
                exame.filas.add(fila)
                exame.filas.add(preferencial)
                exame.create_fila = True
                if exame.verifica:
                    exame.agendamento.participar = True
                    exame.agendamento.save()
                exame.save()

                if exame.agendamento:
                    if exame.agendamento.usuarios.all():
                        #NOTIFICAÇÂO
                        mensagem = 'Atenção, o exame: '+ exame.nome + ' iniciou suas filas, marque seu lugar na fila desejada!'
                        notificacoes.notificacaoAgendamento(request, mensagem, exame.agendamento)

                return redirect('detalhesExame', id=exame.id)
        else:
            context = {
                'msg_error': 'Indisponivel Acessar Essa Área'
            }

            return render(request, 'home.html', {'context': context})

        return render(request, 'cadastro_fila_exame.html', {'form': form})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})


@login_required(login_url='/accounts/login')
def listaFila(request):
    if has_permission(request.user, 'permissao_unidade'):
        unidade = UnidadeSaude.objects.filter(users=request.user)
        filas = [None]
        aux_filas = [None]
        nome = request.GET.get('nome')

        if unidade:

            consultas = unidade[0].consultas.all()

            autorizacoes = unidade[0].autorizacoes.all()

            exames = unidade[0].exames.all()

            if consultas:
                for con in consultas:
                    if con.create_fila:
                        for fila in con.filas.all():
                            filas.append(fila)

            if autorizacoes:
                for aut in autorizacoes:
                    if aut.create_fila:
                        for fila in aut.filas.all():
                            filas.append(fila)

            if exames:
                for ex in exames:
                    if ex.create_fila:
                        for fila in aut.filas.all():
                            filas.append(fila)

            if filas:
                if nome:
                        
                    for fila in filas:
                        if fila and fila.nome == nome:
                            aux_filas.append(fila)
                    
                    if aux_filas:
                        context = {
                            'filas': aux_filas
                        }
                    else:
                        context = {
                            'filas': filas,
                            'msg_busca': 'Nada encontrado para esses parâmetros!'
                        }
                else:
                    context = {
                        'filas': filas
                    }
            else:
                context = {
                    'msg_alert': 'Ainda não possuem Filas'
                }

            return render(request, 'lista_fila.html', {'context': context})

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
def deleteFila(request, id_fila, id_fila_pref):
    if has_permission(request.user, 'permissao_unidade'):
        fila = get_object_or_404(Fila, pk=id_fila)
        fila_pref = get_object_or_404(Fila, pk=id_fila_pref)

        consulta = Consulta.objects.filter(filas=fila)
        autorizacao = Autorizacao.objects.filter(filas=fila)
        exame = Exame.objects.filter(filas=fila)

        if request.method == 'POST':
            if consulta:
                if consulta[0].user == request.user:
                    fila.delete()
                    fila_pref.delete()
                    consulta[0].create_fila = False
                    consulta[0].save()
                    return redirect('detalhesConsulta', id=consulta[0].id)
                
            elif autorizacao:
                if autorizacao[0].user == request.user:
                    fila.delete()
                    fila_pref.delete()
                    autorizacao[0].create_fila = False
                    autorizacao[0].save()
                    return redirect('detalhesAutorizacao', id=autorizacao[0].id)

            elif exame:
                if exame[0].user == request.user:
                    fila.delete()
                    fila_pref.delete()
                    exame[0].create_fila = False
                    exame[0].save()
                    return redirect('detalhesExame', id=exame[0].id)

        return render(request, 'delete_fila.html', {'fila': fila})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})    


@login_required(login_url='/accounts/login')
def detalhesFila(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        fila = get_object_or_404(Fila, pk=id)
        consulta = Consulta.objects.filter(filas=fila)
        autorizacao = Autorizacao.objects.filter(filas=fila)
        exame = Exame.objects.filter(filas=fila)
        fichas = fila.fichas

        if consulta is None and autorizacao is None:
            context = {
                'msg_error': 'Indisponivel Acessar Essa Área'
            }

            return render(request, 'home.html', {'context': context})
        
        elif exame is None:
            context = {
                'msg_error': 'Indisponivel Acessar Essa Área'
            }

            return render(request, 'home.html', {'context': context})
        
        elif consulta:
            if fichas:
                context = {
                    'consulta': consulta[0],
                    'fila': fila,
                    'fichas': fila.fichas
                }

            else:
                context = {
                    'consulta': consulta[0],
                    'fila': fila
                }

        elif autorizacao:
            if fichas:
                context = {
                    'autorizacao': autorizacao[0],
                    'fila': fila,
                    'fichas': fila.fichas
                }

            else:
                context = {
                    'autorizacao': autorizacao[0],
                    'fila': fila
                }
        elif exame:
            if fichas:
                context = {
                    'exame': exame[0],
                    'fila': fila,
                    'fichas': fila.fichas
                }

            else:
                context = {
                    'exame': exame[0],
                    'fila': fila
                }

        contexto.set(context)
        
        return render(request, 'detalhes_fila.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context}) 

@login_required(login_url='/accounts/login')
def naoCompareceu(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        ficha = get_object_or_404(Ficha, pk=id)
        fila = Fila.objects.filter(fichas=ficha)
        consulta = Consulta.objects.filter(filas=fila[0])
        autorizacao = Autorizacao.objects.filter(filas=fila[0])
        exame = Exame.objects.fielter(filas=filas[0])
        
        context = {
            'ficha': ficha,
            'fila': fila[0],
        }

        if request.method == 'POST':
            ficha.status = 'NÃO COMPARECEU'
            ficha.save()

            if consulta:
                if fila[0].fichas.all():
                    context = {
                        'consulta': consulta[0],
                        'fila': fila[0],
                        'fichas': fila[0].fichas.all()
                    }

                else:
                    context = {
                        'consulta': consulta[0],
                        'fila': fila[0]
                    }

            elif autorizacao:
                if fila[0].fichas.all():
                    context = {
                        'autorizacao': autorizacao[0],
                        'fila': fila[0],
                        'fichas': fila[0].fichas.all()
                    }

                else:
                    context = {
                        'autorizacao': autorizacao[0],
                        'fila': fila[0]
                    }
            elif exame:
                if fila[0].fichas.all():
                    context = {
                        'exame': exame[0],
                        'fila': fila[0],
                        'fichas': fila[0].fichas.all()
                    }

                else:
                    context = {
                        'autorizacao': autorizacao[0],
                        'fila': fila[0]
                    }
            return render(request, 'detalhes_fila.html', {'context': context})
        
        return render(request, 'nao_compareceu.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acessar Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})

@login_required(login_url='/accounts/login')
def relatorioFila(request):
    if has_permission(request.user, 'permissao_unidade'):
        html_string = render_to_string('relatorio_fila.html', {'context': contexto.get()})
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        html.write_pdf(target='/tmp/relatorio_fila.pdf', presentational_hints=True)
        fs = FileSystemStorage('/tmp')

        with fs.open('relatorio_fila.pdf') as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="relatorio_fila.pdf'
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


