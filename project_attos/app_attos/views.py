from typing import Any
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import UserProfile, InstagramProfile, Fotos, quantidadeDoadores, Reviews
from .forms import OngForm, ReviewForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

index_page_html = "app_attos/index.html"

def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/perfil/")
    return render(request, index_page_html)


def pagina_da_ong(request, slug):
    usuario = get_object_or_404(User, username=slug)
    user_profile = get_object_or_404(UserProfile, user=usuario)
    profiles = InstagramProfile.objects.filter(user=usuario)
    fotos = Fotos.objects.filter(user=usuario)
    current_datetime = user_profile.last_updated
    descricao_perfil = user_profile.perfil  

    try:
        quantidade_doadores = quantidadeDoadores.objects.get(user=usuario)
        quantidade_doadores_valor = quantidade_doadores.quantidade_doadores
    except quantidadeDoadores.DoesNotExist:
        quantidade_doadores_valor = 0

    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.perfil = user_profile
            review.save()
            return HttpResponseRedirect(request.path_info)
    else:
        review_form = ReviewForm()

    reviews = Reviews.objects.filter(perfil=user_profile)

    return render(request, "pages/page.html", {
        "usuario": usuario,
        "user_profile": user_profile,
        'profiles': profiles,
        'fotos': fotos,
        'quantidade_doadores': quantidade_doadores_valor,
        "descricao_perfil": descricao_perfil,
        'current_datetime': current_datetime,
        'review_form' : review_form,
        'reviews': reviews,
    })

def pagina_de_cadastro(request):
    return render(request, "cadastro/cadastro.html")

@login_required
def pagina_de_perfil(request):
    form = OngForm()
    profiles = instagram_button(request)
    photos = Fotos.objects.filter(user=request.user)
    descricao = descricao_perfil(request)
    return render(request, "perfil/perfil.html", {'form': form, 'profiles': profiles, 'photos': photos, 'descricao': descricao})

@login_required
def descricao_perfil(request):
    perfil_descricao = request.POST.get('perfil')
    if perfil_descricao:
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.last_updated = timezone.now()
        user_profile.perfil = perfil_descricao
        user_profile.save()
        messages.success(request, "Descrição do perfil salva com sucesso.")
    else:
        messages.error(request, "O campo 'descrição do perfil' não pode estar vazio.")
        return redirect('/perfil/')

@login_required
def instagram_button(request):
    if request.method == 'POST':
        instagram_link = request.POST.get('instagram_link')
        nomeRede = request.POST.get('nomeRede')
        last_updated = request.POST.get('last_update')
        if instagram_link:
            instagram_profile = InstagramProfile(user=request.user, instagram_link=instagram_link, nomeRede=nomeRede)
            instagram_profile.save()
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.last_updated = timezone.now()
            user_profile.save()
        else:
            messages.error(request, "O campo 'Instagram Link' não pode estar vazio.")
            return redirect('/perfil/')
    profiles = InstagramProfile.objects.filter(user=request.user)
    return profiles


@login_required
def add_foto(request):
    if request.method == 'POST':
        form = OngForm(request.POST, request.FILES)
        form.instance.user = request.user
        if form.is_valid():
            form.save()
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.last_updated = timezone.now()
            user_profile.save()
    return redirect('pagina_de_perfil')

@login_required
def remover_fotos(request):
    if request.method == 'POST':
        fotos_a_remover = request.POST.getlist('fotos_a_remover')
        if fotos_a_remover:
            Fotos.objects.filter(id__in=fotos_a_remover).delete()
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.last_updated = timezone.now()
            user_profile.save()
    return redirect('pagina_de_perfil')

@login_required
def adicionar_quantidade_doadores(request):
    if request.method == 'POST':
        quantidade = request.POST.get('quantidade_doadores')
        if request.user.is_authenticated:
            quantidade_doadores, created = quantidadeDoadores.objects.get_or_create(user=request.user)
            if quantidade:
                quantidade_doadores.quantidade_doadores += int(quantidade)
                quantidade_doadores.save()
                user_profile = UserProfile.objects.get(user=request.user)
                user_profile.last_updated = timezone.now()
                user_profile.save()
    return redirect('pagina_de_perfil')


from django.contrib.auth.models import User
from django.shortcuts import render, redirect

@require_POST
def cadastrar_usuario(request):
    try:
        usuario_aux = User.objects.get(email=request.POST['email'])
        if usuario_aux:
            return render(request, 'cadastro/cadastro.html', {'msg': 'Erro! Já existe um usuário com o mesmo e-mail'})
    except User.DoesNotExist:
        try:
            nome_usuario = request.POST['nome-usuario']
            usuario_com_nome = User.objects.get(username=nome_usuario)
            if usuario_com_nome:
                return render(request, 'cadastro/cadastro.html', {'msg': 'Erro! Já existe um usuário com o mesmo nome'})
        except User.DoesNotExist:
            nome_usuario = request.POST['nome-usuario']
            email = request.POST['email']
            senha = request.POST['senha']
            novoUsuario = User.objects.create_user(username=nome_usuario, email=email, password=senha)
            novoUsuario.save()
            UserProfile.objects.create(user=novoUsuario, email=email)
            login(request, novoUsuario)
            return redirect("/home")

    return render(request, 'cadastro/cadastro.html', {'msg': 'Erro desconhecido'})


@require_POST
def entrar(request):
    try:
        usuario_aux = User.objects.get(email=request.POST['email'])
    except User.DoesNotExist:
        messages.error(request, "Usuário não existe ou credenciais incorretas")
        return HttpResponseRedirect("/")

    usuario = authenticate(username=usuario_aux.username, password=request.POST["senha"])
    if usuario is not None:
        login(request, usuario)
        return HttpResponseRedirect('/home')
    return HttpResponseRedirect("/")

@login_required
def sair(request):
    logout(request)
    return HttpResponseRedirect("/")

@login_required
def home(request):


    return render(request, "home/home.html")

class atualizarPerfil(UpdateView):
    template_name = "perfil/perfil.html"
    model = UserProfile, InstagramProfile, Fotos, quantidadeDoadores
    fields = ['email', 'instagram_link', 'foto', 'quantidade_doadores']
    success_url = reverse_lazy("page")

    def get_object(self, queryset=None):
        self.object = get_object_or_404(UserProfile, usuario=self.request.user)
