from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserForm, ProfileForm
from .models import Profile, User



@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('sclad:index')
    return render(request, 'accounts/login.html')


def register_view(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.role = request.POST.get('role', 'employee')  # default to 'employee' if role not provided
            user.save()
            return redirect('accounts:create_profile')
    else:
        form = UserForm()
        form.fields['role'] = forms.ChoiceField(choices=User.ROLE_CHOICES)
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('sclad:index')
    else:
        form = ProfileForm(instance=profile)
    return render(request,
                  'accounts/profile.html',
                  {'profile': profile, 'user': request.user})


@login_required
def create_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('accounts:profile')
    else:
        form = ProfileForm()
    return render(request, 'accounts/create_profile.html', {'form': form})

