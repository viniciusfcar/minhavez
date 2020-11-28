from django.shortcuts import render
import onesignal as onesignal_sdk
import requests
import json
from usuario.models import Usuario
from consulta.models import Consulta
from agendamento.models import Agendamento
from datetime import date


def inicioConsultaAutorizacao(request, mensagem, objeto):
    
    fila_normal = None
    fila_preferencial = None
    ids = []

    for fila in objeto.filas.all():
        if fila.fila_preferencial:
            fila_preferencial = fila
        else:
            fila_normal = fila
    
    for ficha in fila_normal.fichas.all():
        ids.append(ficha.usuario.notificacao)
    
    for ficha in fila_preferencial.fichas.all():
        ids.append(ficha.usuario.notificacao)

    header = {"Content-Type": "application/json; charset=utf-8",
        "Authorization": "Basic AAAAYp3wnKU:APA91bF6BbpMdRc6-wvAbfdf76ItATkG9EBz2uDa2BIDWyFYP4tcSU1EgE6pnC-2QbD4sgFvS5_96TDpglzdsD09QTIi9e4lmxOxGfgiJlDwpP-54GEpW_j3tYTcuo7NF9N3Z2IRJvmK"}

    payload = {"app_id": "0414c64c-3f63-486a-8fa2-78ce89f5032e",
            "include_player_ids": ids,
            "headings": {"en": "MinhaVez"},
            "contents": {"en": mensagem}}
    
    req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
    
    print(req.status_code, req.reason)

def avisaPosicaoFila(request, objeto):
    fichas_restante = 0

    for ficha in objeto.fichas.all():
        if ficha.status == 'AGUARDANDO':
            if fichas_restante == 0:
                mensagem = ficha.usuario.user.first_name+' é a sua vez, esteja pronto(a)!'
                
                header = {"Content-Type": "application/json; charset=utf-8",
                    "Authorization": "Basic AAAAYp3wnKU:APA91bF6BbpMdRc6-wvAbfdf76ItATkG9EBz2uDa2BIDWyFYP4tcSU1EgE6pnC-2QbD4sgFvS5_96TDpglzdsD09QTIi9e4lmxOxGfgiJlDwpP-54GEpW_j3tYTcuo7NF9N3Z2IRJvmK"}

                payload = {"app_id": "0414c64c-3f63-486a-8fa2-78ce89f5032e",
                        "include_player_ids": [ficha.usuario.notificacao],
                        "headings": {"en": "MinhaVez"},
                        "contents": {"en": mensagem}}
                
                req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
                
                print(req.status_code, req.reason)
                fichas_restante += 1
            else:
                mensagem = "Faltam "+str(fichas_restante)+" ficha(s) para que você seja atendido, fique atento(a) "+ficha.usuario.user.first_name+"!"

                header = {"Content-Type": "application/json; charset=utf-8",
                    "Authorization": "Basic AAAAYp3wnKU:APA91bF6BbpMdRc6-wvAbfdf76ItATkG9EBz2uDa2BIDWyFYP4tcSU1EgE6pnC-2QbD4sgFvS5_96TDpglzdsD09QTIi9e4lmxOxGfgiJlDwpP-54GEpW_j3tYTcuo7NF9N3Z2IRJvmK"}

                payload = {"app_id": "0414c64c-3f63-486a-8fa2-78ce89f5032e",
                        "include_player_ids": [ficha.usuario.notificacao],
                        "headings": {"en": "MinhaVez"},
                        "contents": {"en": mensagem}}
                
                req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
                
                print(req.status_code, req.reason)
                fichas_restante += 1

def notificacaoIndividual(request, mensagem, usuario):
    
    header = {"Content-Type": "application/json; charset=utf-8",
        "Authorization": "Basic AAAAYp3wnKU:APA91bF6BbpMdRc6-wvAbfdf76ItATkG9EBz2uDa2BIDWyFYP4tcSU1EgE6pnC-2QbD4sgFvS5_96TDpglzdsD09QTIi9e4lmxOxGfgiJlDwpP-54GEpW_j3tYTcuo7NF9N3Z2IRJvmK"}

    payload = {"app_id": "0414c64c-3f63-486a-8fa2-78ce89f5032e",
            "include_player_ids": [usuario.notificacao],
            "headings": {"en": "MinhaVez"},
            "contents": {"en": mensagem}}
    
    req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
    
    print(req.status_code, req.reason)

def notificacaoColetiva(request, mensagem, objeto):

    ids = []

    for obj in objeto:
        ids.append(obj.usuario.notificacao)

    header = {"Content-Type": "application/json; charset=utf-8",
        "Authorization": "Basic AAAAYp3wnKU:APA91bF6BbpMdRc6-wvAbfdf76ItATkG9EBz2uDa2BIDWyFYP4tcSU1EgE6pnC-2QbD4sgFvS5_96TDpglzdsD09QTIi9e4lmxOxGfgiJlDwpP-54GEpW_j3tYTcuo7NF9N3Z2IRJvmK"}

    payload = {"app_id": "0414c64c-3f63-486a-8fa2-78ce89f5032e",
            "include_player_ids": ids,
            "headings": {"en": "MinhaVez"},
            "contents": {"en": mensagem}}
    
    req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
    
    print(req.status_code, req.reason) 

def notificacaoAgendamento(request, mensagem, objeto):
    
    ids = []

    for usuario in objeto.usuarios.all():
        ids.append(usuario.notificacao)

    header = {"Content-Type": "application/json; charset=utf-8",
        "Authorization": "Basic AAAAYp3wnKU:APA91bF6BbpMdRc6-wvAbfdf76ItATkG9EBz2uDa2BIDWyFYP4tcSU1EgE6pnC-2QbD4sgFvS5_96TDpglzdsD09QTIi9e4lmxOxGfgiJlDwpP-54GEpW_j3tYTcuo7NF9N3Z2IRJvmK"}

    payload = {"app_id": "0414c64c-3f63-486a-8fa2-78ce89f5032e",
            "include_player_ids": ids,
            "headings": {"en": "MinhaVez"},
            "contents": {"en": mensagem}}
    
    req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
    
    print(req.status_code, req.reason)
