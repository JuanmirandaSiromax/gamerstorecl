from django.urls import path
from . import  views

urlpatterns =[
    path ('juegos/', views.listado_juegos_api, name='listado_juegos_api'),
    path ('juegos/<int:id>/', views.vista_juegos_api, name='vista_juegos_api'),
    path ('juegos/detalle_juego_api/', views.detalle_juego_api, name='detalle_juego_api'),
    path ('juegos/personajes_juego/', views.personajes_juego_api, name='personajes_juego_api'),
]