from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login 
from .forms import CreatUser

# Create your views here.
def signup(request):
    form = CreatUser()
    if request.method == "POST":
        form = CreatUser(request.POST)
        if form.is_valid():
            form.save()
            redirect("login_page")
    return render(request, 'signup_page.html', {'form': form})

def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password = password)
        if user is not None:
            login(request, user)
            return redirect('/home')
    return render(request, 'login_page.html')