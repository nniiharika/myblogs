from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),  # This URL should work
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
]