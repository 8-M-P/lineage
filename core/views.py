from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import render, redirect

from .forms import LoginForm
from .models import *


@login_required
def home(request, tag: str = None):
    if tag is not None:
        try:
            table = Media.objects.filter(user_tag__last_name__contains=tag)
        except ObjectDoesNotExist:
            raise Http404
    else:
        table = Media.objects.all()

    tags: list[str] = []
    for row in table:
        for i in row.user_tag.all():
            tags.append(i.last_name.lower())
    tags = list(set(tags))
    context = {
        'table': table,
        'current_tag': tag,
        'tags': tags,
    }
    return render(request, 'pages/home.html', context)


@login_required
def users(request, tag: str = None):
    if tag is not None:
        try:
            table = User.objects.filter(last_name__contains=tag)
        except ObjectDoesNotExist:
            raise Http404
    else:
        table = User.objects.all()
    tags: list[str] = []
    for row in table:
        tags.append(row.last_name.lower())
    tags = list(set(tags))

    context = {
        'table': table,
        'current_tag': tag,
        'tags': tags
    }
    return render(request, 'pages/users.html', context)


@login_required
def single_user(request, pk=None, family: bool = None):
    if pk is None:
        user = User.objects.get(id=request.user.pk)
    else:
        user = User.objects.get(id=pk)

    images_query = Q(user_tag=user.pk)
    children = User.objects.filter(Q(father=user.pk) | Q(mother=user.pk))
    spouse = None

    if children.exists():
        if children.first().mother is not None:
            if children.first().mother == user:
                spouse = children.first().father

        if children.first().father is not None:
            if children.first().father == user:
                spouse = children.first().mother

        if family is True:
            if spouse is not None:
                images_query |= Q(user_tag=spouse.pk)
            for child in children:
                images_query |= Q(user_tag=child.pk)
    else:
        spouse = None
        children = None

    if user.father is not None and user.mother is not None:
        siblings_query = Q(mother=user.mother.pk) | Q(father=user.father.pk)
        if family is True:
            images_query |= Q(user_tag=user.mother.pk) | Q(user_tag=user.father.pk)
    elif user.father is None and user.mother is not None:
        siblings_query = Q(mother=user.mother.pk)
        if family is True:
            images_query |= Q(user_tag=user.mother.pk)
    elif user.father is not None and user.mother is None:
        siblings_query = Q(father=user.father.pk)
        if family is True:
            images_query |= Q(user_tag=user.father.pk)
    else:
        siblings_query = None

    if siblings_query is not None:
        siblings_table = User.objects.filter(siblings_query)
        if siblings_table.exists():
            siblings = siblings_table
        else:
            siblings = None
    else:
        siblings = None

    images = Media.objects.filter(images_query).distinct()
    context = {
        'user': user,
        'images': images,
        'siblings': siblings,
        'children': children,
        'spouse': spouse,
    }
    return render(request, 'pages/single.html', context)


def logout_page(request):
    if request.user.is_authenticated:
        if request.user.has_admin_permit:
            u = User.objects.get(pk=request.user.pk)
            u.has_admin_permit = False
            u.save(update_fields=['has_admin_permit'])
    messages.success(request, 'Çıkış başarılı.')
    logout(request)
    return redirect("login_page")


def login_page(request):
    if request.user.is_authenticated:
        if not request.user.is_superuser:
            if request.user.has_admin_permit:
                return redirect('home')
            else:
                if RequestedUserPermitLog.objects.filter(user=request.user, status=True).exists():
                    messages.error(request, 'İzin başvurunuz açık durumdadır, Lütfen Yönetici ile iletişime geçin.')
                else:
                    u = RequestedUserPermitLog(user=request.user)
                    messages.error(request, 'Gerekli izine sahip değilsiniz, Lütfen Yönetici ile iletişime geçin.')
                return redirect('login_page')
        else:
            return redirect('home')

    if request.method == 'POST':
        if not request.POST['full_name']:
            raise PermissionDenied
        if not request.POST['password']:
            raise PermissionDenied

        full_name = request.POST['full_name']
        password = request.POST['password']
        user = auth.authenticate(username=full_name, password=password)
        if user is not None:
            if user.is_superuser:
                auth.login(request, user)
                return redirect('home')
            elif user.has_admin_permit:
                auth.login(request, user)
                return redirect('home')
            else:
                if RequestedUserPermitLog.objects.filter(user=user, status=True).exists():
                    messages.error(request, 'İzin başvurunuz açık durumdadır, Lütfen Yönetici ile iletişime geçin.')
                else:
                    u = RequestedUserPermitLog(user=user)
                    u.save()
                    messages.error(request, 'Gerekli izine sahip değilsiniz, Lütfen Yönetici ile iletişime geçin.')
                return redirect('login_page')
        else:
            messages.error(request, 'Kullanıcı Adı yada Şifre yanlış.')
            return redirect('login_page')
    else:
        form = LoginForm()
        return render(request, 'pages/login.html', {'form': form})
