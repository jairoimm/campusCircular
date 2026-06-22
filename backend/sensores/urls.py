from django.urls import path
from . import views

urlpatterns = [
    path('lectura/',                       views.recibir_lectura,   name='lectura'),
    path('estado/',                        views.estado_contenedores, name='estado'),
    path('alertas/',                       views.alertas_activas,   name='alertas'),
    path('alertas/<int:alerta_id>/atender/', views.atender_alerta,  name='atender-alerta'),
]