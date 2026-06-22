from django.urls import path
from . import views

urlpatterns = [
    path('contenedor/<uuid:codigo_qr>/', views.contenedor_por_qr,  name='contenedor-qr'),
    path('registrar/',                   views.registrar_deposito,  name='registrar'),
    path('mis-registros/',               views.mis_registros,       name='mis-registros'),
]