from django.shortcuts import render


def homepage_render(request):
    return render(request, 'homepage.html')
