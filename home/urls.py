from django.urls import path
from .views import homeUnidadeSaude
from .views import homeUsuario
from .views import homeAdm
from .views import filasIniciadas
from .views import chamarFichaNormalConsulta
from .views import atenderFicha
from .views import chamarFichaPreferencialConsulta
from .views import chamarFichaNormalAutorizacao
from .views import chamarFichaPreferencialAutorizacao

urlpatterns = [
    path('home_unidade_saude/', homeUnidadeSaude, name='homeUnidadeSaude'),
    path('home_usuario/', homeUsuario, name='homeUsuario'),
    path('home_adm/', homeAdm, name='homeAdm'),
    path('filas_iniciadas/', filasIniciadas, name='filasIniciadas'),
    path('chamar_ficha_normal_consulta/<int:id>/', chamarFichaNormalConsulta, name='chamarFichaNormalConsulta'),
    path('atender_ficha/<int:id>/', atenderFicha, name='atenderFicha'),
    path('chamar_ficha_preferencial_consulta/<int:id>/', chamarFichaPreferencialConsulta, name='chamarFichaPreferencialConsulta'),
    path('chamar_ficha_normal_autorizacao/<int:id>/', chamarFichaNormalAutorizacao, name='chamarFichaNormalAutorizacao'),
    path('chamar_ficha_preferencial_autorizacao/<int:id>/', chamarFichaPreferencialAutorizacao, name='chamarFichaPreferencialAutorizacao')
]