"""
URL configuration for restaurants app
"""

from django.urls import path
from . import views

app_name = 'restaurants'

urlpatterns = [
    # Authentication
    path('auth/signup/', views.register_restaurant, name='register'),
    path('auth/login/', views.login_restaurant, name='login'),
    path('auth/logout/', views.logout_restaurant, name='logout'),

    # Restaurant Profile
    path('profile/', views.restaurant_profile, name='profile'),
    path('qr/', views.restaurant_qr_code, name='qr_code'),

    # Table Management
    path('tables/', views.table_list_create, name='table_list_create'),
    path('tables/<int:pk>/', views.table_detail, name='table_detail'),

    # Public endpoints
    path('public/<uuid:qr_code_id>/info/', views.public_restaurant_info, name='public_info'),
    path('public/<uuid:qr_code_id>/tables/', views.public_restaurant_tables, name='public_tables'),
]
