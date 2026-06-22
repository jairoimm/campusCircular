from django.urls import path
from . import views

urlpatterns = [
    path('mis-puntos/', views.mis_puntos, name='mis-puntos'),
    path('beneficios/', views.lista_beneficios, name='beneficios'),
    path('canjear/', views.solicitar_canje, name='canjear'),
    path('canje/<int:canje_id>/aprobar/', views.aprobar_canje, name='aprobar-canje'),
    path('dashboard/', views.dashboard_data, name='dashboard'),
]