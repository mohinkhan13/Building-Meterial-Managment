from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,'index.html')

def register(request):
    return render(request,'register.html')

def login(request):
    return render(request,'login.html')

def forgot_password(request):
    return render(request,'forgot-password.html')

def change_password(request):
    return render(request,'change-password.html')

def user_profile(request):
    return render(request,'user-profile.html')

def logout(request):
    return render(request,'login.html')

def contact(request):
    return render(request,'contact.html')