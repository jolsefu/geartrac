from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout

def index(request):
    return HttpResponse("Hello, there")

def home(request):
    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    return redirect('/')
