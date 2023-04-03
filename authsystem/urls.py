from django.urls import path 
from . import views
from . views import PasswordResetView

urlpatterns = [
    path('home/',views.home, name='home' ),
    path('', views.LoginUser, name='signin'),
    path('register/', views.register, name='register'),
    path('sendqrcode/', views.QRCodeView, name='qrcode'),
    path('AuthenticateUser/', views.AuthenticateUser, name='authenticate'),
    path('resetpassword/',PasswordResetView.as_view(), name='resetpassword')
]