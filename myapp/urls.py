from django.urls import path
from .views import *
urlpatterns = [
    path('', index , name='index'),
    path('register/', register , name='register'),
    path('login/', login , name='login'),
    path('logout/', logout , name='logout'),
    path('contact/', contact , name='contact'),
    path('forgot-password/', forgot_password , name='forgot-password'),
    path('change-password', change_password , name='change-password'),
    path('user-profile', user_profile , name='user-profile'),
    
]