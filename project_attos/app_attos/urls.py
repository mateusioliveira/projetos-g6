from django.urls import path
from django.contrib import admin
from django.urls import include
from . import views

urlpatterns = [
    path("cadastrar/", views.pagina_de_cadastro, name='cadastrar'), # rota de pagina do usuario
    path("cadastrar_usuario/", views.cadastrar_usuario, name='cadastrar_usuario'), # url de submissao do form
    path("", views.index, name="index"),
    path('instagram_button/', views.instagram_button, name='instagram_button'),
    path("entrar/", views.entrar, name='entrar'),
    path("sair/", views.sair, name='sair'),
    path("perfil/", views.pagina_de_perfil, name='pagina_de_perfil'),
    path("ong/<str:slug>/", views.pagina_da_ong, name='pagina_da_ong')
]
