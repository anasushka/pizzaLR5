import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import RegisterForm, LoginForm, UserProfileForm
from .models import UserProfile

logger = logging.getLogger('users')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            UserProfile.objects.create(
                user=user,
                birth_date=form.cleaned_data['birth_date'],
                phone=form.cleaned_data['phone'],
                role=form.cleaned_data['role'],
            )
            login(request, user)
            logger.info(f'New user registered: {user.username}')
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
        else:
            logger.warning(f'Registration form invalid: {form.errors}')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f'User logged in: {user.username}')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            logger.warning('Failed login attempt')
            messages.error(request, 'Неверный логин или пароль.')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    logger.info(f'User logged out: {request.user.username}')
    logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            p = form.save(commit=False)
            p.user = request.user
            p.save()
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.email = form.cleaned_data.get('email', '')
            request.user.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect('profile')
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = UserProfileForm(instance=profile, initial=initial)

    return render(request, 'users/profile.html', {'form': form, 'profile': profile})


@login_required
def dashboard_view(request):
    from shop.models import Order
    profile = getattr(request.user, 'profile', None)
    context = {'profile': profile}

    if request.user.is_superuser:
        context['orders'] = Order.objects.order_by('-created_at')[:20]
    elif profile and profile.role == 'employee':
        context['orders'] = Order.objects.filter(
            status__in=['new', 'preparing', 'delivering']
        ).order_by('-created_at')[:20]
    else:
        context['orders'] = Order.objects.filter(
            client=profile
        ).order_by('-created_at') if profile else []

    return render(request, 'users/dashboard.html', context)

