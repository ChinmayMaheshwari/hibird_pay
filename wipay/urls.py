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
from django.conf.urls.static import static
from userpay import views
from .import settings
from rest_framework.authtoken.views import obtain_auth_token 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/password_reset/',auth_views.PasswordResetView.as_view(),name='admin_password_reset'),
    path('admin/password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(success_url='/login/'),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    path('password_reset/',auth_views.PasswordResetView.as_view(template_name='login.html',success_url = '/login/?success=Password reset link sent to your given email id'),name='change_password'),
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('profile/',views.profile,name='profile'),
    path('payment/',views.payment,name='payment'),
    path('contact/',views.contactForm,name='contact'),
    path('',include("django.contrib.auth.urls")),
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    path('api/profile/', views.PersonalInfoView.as_view(), name='api_profile'),
    path('api/payment/', views.PaymentInfoView.as_view(), name='api_payment'),
    path('api/transaction/',views.TransactionView.as_view({'get': 'list'}),name='transaction'),
    path('api/slider/',views.SliderView.as_view({'get': 'list'}),name='slider'),
    path('api/plandetail/',views.PlanView.as_view({'get': 'list'}),name='plandetail'),
    path('invoice/<int:tid>/',views.generateInvoice,name='invoice'),
    path('api/forgot/',views.ForgotPasswordView.as_view(),name='forgot_api'),   
] + static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)