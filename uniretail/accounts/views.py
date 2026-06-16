from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from .models import CustomUser


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        if user.role == CustomUser.Role.VENDOR:
            messages.info(
                request,
                'Your vendor account has been created and is pending admin approval. '
                'You will be notified once approved.'
            )
            return redirect('accounts:login')
        else:
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name or user.username}!')
            return redirect('dashboard:home')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        # Block unapproved vendors
        if user.role == CustomUser.Role.VENDOR and not user.is_approved_vendor:
            messages.error(
                request,
                'Your vendor account is awaiting admin approval. Please check back later.'
            )
            return redirect('accounts:login')
        login(request, user)
        next_url = request.GET.get('next', 'dashboard:home')
        return redirect(next_url)

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    form = ProfileUpdateForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {'form': form})
