from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Agendamento
from .forms import FormAgendamento
from usuario.models import Usuario
from autorizacao.models import Autorizacao
from consulta.models import Consulta
from exame.models import Exame
from unidadeSaude.models import UnidadeSaude
from rolepermissions.checkers import has_permission
from rest_framework import viewsets
from .serializers import AgendamentoSerializer
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from rest_framework.decorators import action
from rest_framework.response import Response
import json
from django.core import serializers
from notificacoes import views as notificacoes


class GetAgendamentoViewSet(viewsets.ModelViewSet):
    serializer_class = AgendamentoSerializer

    def get_queryset(self):
        queryset = Agendamento.objects.all()
        return queryset

    @action(methods=['get'], detail=True)
    def agendamento_usuario(self, request, pk=None):
        usuario = get_object_or_404(Usuario, pk=pk)
        agendamentos = Agendamento.objects.filter(usuarios=usuario)
        tmpJson = serializers.serialize("json", agendamentos)
        tmpObj = json.loads(tmpJson)
        return HttpResponse(json.dumps(tmpObj))

    @action(methods=['get'], detail=True)
    def detalhes_agendamento(self, request, pk=None):
        agendamento = get_object_or_404(Agendamento, pk=pk)
        consulta = Consulta.objects.filter(agendamento=agendamento)
        autorizacao = Autorizacao.objects.filter(agendamento=agendamento)
        aux = None
        if consulta:
            aux = consulta
        elif autorizacao:
            aux = autorizacao
            
        tmpJson = serializers.serialize("json", aux)
        tmpObj = json.loads(tmpJson)
        return HttpResponse(json.dumps(tmpObj))

@login_required(login_url='/accounts/login')
def cadastroAgendamentoConsulta(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        consulta = get_object_or_404(Consulta, pk=id)

        if consulta.user == request.user:
            if request.method == 'POST':

                agendamento = Agendamento(nome=request.POST.get('nome'), vagas=request.POST.get('vagas'))
                agendamento.save()
                consulta.agendamento = agendamento
                consulta.verifica = True
                consulta.save()
                return redirect('detalhesAgendamento', id=agendamento.id)
            else:
                form = FormAgendamento()

            context = {
                'consulta': consulta,
                'form': form,
            }
        else:
            context = {
                'msg_error': 'Indisponivel Acessar Essa Área'

            }
            return redirect('homeUnidadeSaude', {'context': context})
    else:
        context = {
            'msg_error': 'Sem Permissão Para Essa Área'

        }
        return redirect('homeUsuario', {'context': context})

    return render(request, 'cadastro_agendamento_consulta.html', {'context': context})

@login_required(login_url='/accounts/login')
def cadastroAgendamentoAutorizacao(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        autorizacao = get_object_or_404(Autorizacao, pk=id)

        if autorizacao.user == request.user:
            if request.method == 'POST':

                agendamento = Agendamento(nome=request.POST.get('nome'), vagas=request.POST.get('vagas'))
                agendamento.save()
                autorizacao.agendamento = agendamento
                autorizacao.verifica = True
                autorizacao.save()
                return redirect('detalhesAgendamento', id=agendamento.id)
            else:
                form = FormAgendamento()

            context = {
                'autorizacao': autorizacao,
                'form': form,
            }
        else:
            context = {
                'msg_error': 'Indisponivel Acessar Essa Área'

            }
            return redirect('homeUnidadeSaude', {'context': context})
    else:
        context = {
            'msg_error': 'Sem Permissão Para Essa Área'

        }
        return redirect('homeUsuario', {'context': context})

    return render(request, 'cadastro_agendamento_autorizacao.html', {'context': context})

@login_required(login_url='/accounts/login')
def cadastroAgendamentoExame(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        exame = get_object_or_404(Exame, pk=id)

        if exame.user == request.user:
            if request.method == 'POST':

                agendamento = Agendamento(nome=request.POST.get('nome'), vagas=request.POST.get('vagas'))
                agendamento.save()
                exame.agendamento = agendamento
                exame.verifica = True
                exame.save()
                return redirect('detalhesAgendamento', id=agendamento.id)
            else:
                form = FormAgendamento()

            context = {
                'exame': exame,
                'form': form,
            }
        else:
            context = {
                'msg_error': 'Indisponivel Acessar Essa Área'

            }
            return redirect('homeUnidadeSaude', {'context': context})
    else:
        context = {
            'msg_error': 'Sem Permissão Para Essa Área'

        }
        return redirect('homeUsuario', {'context': context})

    return render(request, 'cadastro_agendamento_exame.html', {'context': context})


@login_required(login_url='/accounts/login')
def listaAgendamento(request):
    if has_permission(request.user, 'permissao_unidade'):
        unidade = UnidadeSaude.objects.filter(users=request.user)
        agendamentos = []
        aux_agendamentos = []
        nome = request.GET.get('nome')

        if unidade:
            consultas = unidade[0].consultas.all()
            autorizacoes = unidade[0].autorizacoes.all()

            if consultas:
                for con in consultas:
                    if con.agendamento:
                        agendamentos.append(con.agendamento)

            if autorizacoes:
                for aut in autorizacoes:
                    if aut.agendamento:
                        agendamentos.append(aut.agendamento)

            if agendamentos:
                if nome:
                    
                    for ag in agendamentos:
                        if ag and ag.nome == nome:
                            aux_agendamentos.append(ag)
                    
                    if aux_agendamentos:
                        context = {
                            'agendamentos': aux_agendamentos
                        }
                    else:
                        context = {
                            'agendamentos': agendamentos,
                            'msg_busca': 'Nada encontrado para esses parâmetros!'
                        }
                else:
                    context = {
                        'agendamentos': agendamentos
                    }

            else:
                 context = {
                    'msg_alert': 'Ainda não possuem Agendamentos'
                }

            return render(request, 'lista_agendamento.html', {'context': context})

        else:
            context = {
                'msg_error': 'Indisponivel Acessar Essa Área'
            }
    else:
        context = {
            'msg_error': 'Sem Permissão Para Essa Área'

        }
        return render(request, 'home_usuario.html', {'context': context})


@login_required(login_url='/accounts/login')
def deleteAgendamento(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        agendamento = get_object_or_404(Agendamento, pk=id)
        consulta = Consulta.objects.filter(agendamento=agendamento)
        autorizacao = Autorizacao.objects.filter(agendamento=agendamento)
        exame = Exame.objects.filter(agendamento=agendamento)

        if request.method == 'POST':
            if consulta:
                if consulta[0].user == request.user:
                    agendamento.delete()
                    return redirect('detalhesConsulta', id=consulta[0].id)
                else:
                    context = {
                        'msg_error': 'Indisponivel Acessar Essa Área'
                    }

                    return redirect('homeUnidadeSaude', {'context': context})
            
            elif autorizacao:
                if autorizacao[0].user == request.user:
                    agendamento.delete()
                    return redirect('detalhesAutorizacao', id=autorizacao[0].id)
            
            elif exame:
                if exame[0].user == request.user:
                    agendamento.delete()
                    return redirect('detalhesExame', id=exame[0].id)

        return render(request, 'delete_agendamento.html', {'agendamento': agendamento})
    else:
        context = {
            'msg_error': 'Sem Permissão Para Essa Área'
        }

        return render(request, 'home_usuario.html', {'context': context})


@login_required(login_url='/accounts/login')
def detalhesAgendamento(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        agendamento = get_object_or_404(Agendamento, pk=id)
        usuarios = agendamento.usuarios
        consulta = Consulta.objects.filter(agendamento=agendamento)
        exame = Exame.objects.filter(agendamento=agendamento)
        autorizacao = Autorizacao.objects.filter(agendamento=agendamento)
    
        if consulta:
            context = {
                'agendamento': agendamento,
                'usuarios': usuarios,
                'consulta': consulta[0],
            }
        elif autorizacao:
            context = {
                'agendamento': agendamento,
                'usuarios': usuarios,
                'autorizacao': autorizacao[0],
            }
        elif exame:
            context = {
                'agendamento': agendamento,
                'usuarios': usuarios,
                'exame': exame[0],
            }

        contexto.set(context)

        return render(request, 'detalhes_agendamento.html', {'context': context})
    else:
        context = {
            'msg_error': 'Sem Permissão Para Essa Área'
        }

        return render(request, 'home_usuario.html', {'context': context})

    return render(request, 'detalhes_agendamento.html', {'context': context})


@login_required(login_url='/accounts/login')
def adicionaUsuarioAgendamento(request, id):
    if has_permission(request.user, 'permissao_unidade'):
        agendamento = get_object_or_404(Agendamento, pk=id)
        consulta = Consulta.objects.filter(agendamento=agendamento)
        autorizacao = Autorizacao.objects.filter(agendamento=agendamento)
        exame = Exame.objects.filter(agendamento=agendamento)

        cpf = request.GET.get('cpf')
        usuario = Usuario.objects.filter(cpf=cpf)
        na_fila = False

        for user in agendamento.usuarios.all():
            if user == usuario[0]:
                na_fila = True

        if consulta:
            if consulta[0].user == request.user:
                if usuario and na_fila == False:
                    if agendamento.vagas > 0:
                        agendamento.usuarios.add(usuario[0])
                        agendamento.vagas -= 1
                        agendamento.save()
                        context = {
                            'agendamento': agendamento,
                            'usuarios': agendamento.usuarios,
                            'consulta': consulta[0],
                        }
                    else:
                        context = {
                            'agendamento': agendamento,
                            'usuarios': agendamento.usuarios,
                            'msg_vagas': 'Vagas excedidas.',
                            'consulta': consulta[0],
                        }
                else:
                    context = {
                        'agendamento': agendamento,
                        'usuarios': agendamento.usuarios,
                        'msg_usuario': 'Usuário não localizado ou já está nesse agendamento.',
                        'consulta': consulta[0],
                    }
            else:
                context = {
                    'msg_error': 'Indisponivel Acessar Essa Área'
                }

                return redirect('homeUnidadeSaude', {'context': context})
        elif autorizacao:
            if autorizacao[0].user == request.user:
                if usuario and na_fila == False:
                    if agendamento.vagas > 0:
                        agendamento.usuarios.add(usuario[0])
                        agendamento.vagas -= 1
                        agendamento.save()
                        context = {
                            'agendamento': agendamento,
                            'usuarios': agendamento.usuarios,
                            'autorizacao': autorizacao[0],
                        }
                    else:
                        context = {
                            'agendamento': agendamento,
                            'usuarios': agendamento.usuarios,
                            'msg_vagas': 'Vagas excedidas.',
                            'autorizacao': autorizacao[0],
                        }
                else:
                    context = {
                        'agendamento': agendamento,
                        'usuarios': agendamento.usuarios,
                        'msg_usuario': 'Usuário não localizado ou já está nesse agendamento.',
                        'autorizacao': autorizacao[0],
                    }
            else:
                context = {
                    'msg_error': 'Indisponivel Acessar Essa Área'
                }

                return redirect('homeUnidadeSaude', {'context': context})
        elif exame:
            if exame[0].user == request.user:
                if usuario and na_fila == False:
                    if agendamento.vagas > 0:
                        agendamento.usuarios.add(usuario[0])
                        agendamento.vagas -= 1
                        agendamento.save()
                        context = {
                            'agendamento': agendamento,
                            'usuarios': agendamento.usuarios,
                            'exame': exame[0],
                        }
                    else:
                        context = {
                            'agendamento': agendamento,
                            'usuarios': agendamento.usuarios,
                            'msg_vagas': 'Vagas excedidas.',
                            'exame': exame[0],
                        }
                else:
                    context = {
                        'agendamento': agendamento,
                        'usuarios': agendamento.usuarios,
                        'msg_usuario': 'Usuário não localizado ou já está nesse agendamento.',
                        'exame': exame[0],
                    }
            else:
                context = {
                    'msg_error': 'Indisponivel Acessar Essa Área'
                }

                return redirect('homeUnidadeSaude', {'context': context})

        #NOTIFICAÇÂO
        mensagem = usuario[0].user.first_name+' você foi adicionado no agendamento: '+agendamento.nome+'!'
        notificacoes.notificacaoIndividual(request, mensagem, usuario[0])

        return render(request, 'detalhes_agendamento.html', {'context': context})
    else:
        context = {
            'msg_error': 'Sem Permissão Para Essa Área'
        }
        return render(request, 'home_usuario.html', {'context': context})

@login_required(login_url='/accounts/login')
def excluiUsuarioAgendamento(request, idUser, id):
    if has_permission(request.user, 'permissao_unidade'):
        agendamento = get_object_or_404(Agendamento, pk=id)
        usuario = get_object_or_404(Usuario, pk=idUser)
        consulta = Consulta.objects.filter(agendamento=agendamento)
        autorizacao = Autorizacao.objects.filter(agendamento=agendamento)
        exame = Exame.objects.filter(agendamento=agendamento)

        if request.method == 'POST':
            if consulta:
                if consulta[0].user == request.user:
                    if usuario:
                        agendamento.usuarios.remove(usuario)
                        agendamento.vagas += 1
                        agendamento.save()
                else:
                    context = {
                        'msg_error': 'Indisponivel Acessar Essa Área'
                    }

                    return redirect('homeUnidadeSaude', {'context': context})
            elif autorizacao:
                if autorizacao[0].user == request.user:
                    if usuario:
                        agendamento.usuarios.remove(usuario)
                        agendamento.vagas += 1
                        agendamento.save()
                else:
                    context = {
                        'msg_error': 'Indisponivel Acessar Essa Área'
                    }

                    return redirect('homeUnidadeSaude', {'context': context})
            
            elif exame:
                if exame[0].user == request.user:
                    if usuario:
                        agendamento.usuarios.remove(usuario)
                        agendamento.vagas += 1
                        agendamento.save()
                else:
                    context = {
                        'msg_error': 'Indisponivel Acessar Essa Área'
                    }

                    return redirect('homeUnidadeSaude', {'context': context})
            
            #NOTIFICAÇÂO
            mensagem = usuario.user.first_name+' você foi excluido do agendamento: '+agendamento.nome+'. Para mais informações entre em contato com a Unidade de Saúde!'
            notificacoes.notificacaoIndividual(request, mensagem, usuario)

            return redirect('detalhesAgendamento', id=agendamento.id)

        context = {
            'agendamento': agendamento,
            'usuarios': agendamento.usuarios,
            'usuario': usuario,
        }

        return render(request, 'exclui_usuario_agendamento.html', {'context': context})
    else:
        context = {
            'msg_error': 'Indisponivel Acessar Essa Área'
        }

@login_required(login_url='/accounts/login')
def detalhesAgendamentoUsuario(request, id):
    if has_permission(request.user, 'permissao_usuario'):
        agendamento = get_object_or_404(Agendamento, pk=id)
        consulta = Consulta.objects.filter(agendamento=agendamento)
        autorizacao = Autorizacao.objects.filter(agendamento=agendamento)
        exame = Exame.objects.filter(agendamento=agendamento)
        
        if consulta:
            context = {
                'agendamento': agendamento,
                'consulta': consulta[0],
            }
        elif autorizacao:
            context = {
                'agendamento': agendamento,
                'autorizacao': autorizacao[0],
            }
        
        elif exame:
            context = {
                'agendamento': agendamento,
                'exame': exame[0],
            }
        return render(request, 'detalhes_agendamento_usuario.html', {'context': context})
    else:
        context = {
            'msg_error': 'Impossivel Acesssar Essa Área'
        }
        return render(request, 'home.html', {'context': context})

@login_required(login_url='/accounts/login')
def relatorioAgendamento(request):
    if has_permission(request.user, 'permissao_unidade'):
        html_string = render_to_string('relatorio_agendamento.html', {'context': contexto.get()})
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        html.write_pdf(target='/tmp/relatorio_agendamento.pdf', presentational_hints=True)
        fs = FileSystemStorage('/tmp')

        with fs.open('relatorio_agendamento.pdf') as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="relatorio_agendamento.pdf'
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

