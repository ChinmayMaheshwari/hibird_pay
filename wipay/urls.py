"""wipay URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.views.generic import TemplateView
from userpay import views
from rest_framework.authtoken.views import obtain_auth_token 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('profile/',views.profile,name='profile'),
    path('payment/',views.payment,name='payment'),
    path('',include("django.contrib.auth.urls")),
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    path('api/profile/', views.PersonalInfoView.as_view(), name='profile'),
    path('api/payment/', views.PaymentInfoView.as_view(), name='payment'),
       
]
