"""
URL configuration for core app
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Page views
    path('login/', views.login_page, name='login_page'),
    path('signup/', views.signup_page, name='signup_page'),
    path('owner-dashboard/', views.owner_dashboard_page, name='owner_dashboard'),
    path('admin-dashboard/', views.admin_dashboard_page, name='admin_dashboard'),

    # API endpoints
    path('api/auth/signup/', views.signup, name='signup'),
    path('api/auth/login/', views.login, name='login'),
    path('api/auth/logout/', views.logout, name='logout'),
    path('api/auth/me/', views.current_user, name='current_user'),
]
