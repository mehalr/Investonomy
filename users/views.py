from django.shortcuts import render, redirect
from users.forms import UserRegistrationForm, UserAuthenticationForm
from django.contrib.auth import login, logout, authenticate


def user_register(request):
    context = {}
    if request.user.is_authenticated:
        return redirect('finance:dashboard')
    if request.POST:
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user.set_password(password)
            user.save()
            account = authenticate(username=username, password=password)
            login(request, account)
            return redirect('finance:dashboard')
        else:
            print(form.errors)
            context['form'] = form
    return render(request, 'signup.html', context)


def user_login(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        return redirect('finance:dashboard')
    if request.POST:
        form = UserAuthenticationForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('finance:dashboard')
        else:
            context['error'] = form.errors
    return render(request, 'signin.html')


def user_reset_password(request):
    return render(request, 'reset_password.html')


def user_logout(request):
    logout(request)
    return redirect('homepage')
