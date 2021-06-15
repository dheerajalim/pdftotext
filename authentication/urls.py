from django.urls import path
from .views import LoginAPIView, RegisterAPIView, RegistrationView, LoginView, LogoutView

app_name = 'authentication'

urlpatterns = [

    path('register', RegistrationView.as_view(), name='user_registration'),
    path('login', LoginView.as_view(), name='user_login'),
    path('logout', LogoutView.as_view(), name='user_logout'),

    # Register User API
    path('api/register', RegisterAPIView.as_view(), name='user_registration_api'),
    # Login User API
    path('api/login', LoginAPIView.as_view(), name='user_login_api')
]

