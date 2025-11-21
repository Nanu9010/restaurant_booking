"""
URL configuration for bookings app
"""

from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Public booking endpoints
    path('public/<uuid:qr_code_id>/availability/', views.check_availability, name='check_availability'),
    path('public/<uuid:qr_code_id>/book/', views.create_booking, name='create_booking'),

    # Restaurant owner dashboard endpoints
    path('', views.booking_list, name='booking_list'),
    path('today/', views.today_bookings, name='today_bookings'),
    path('stats/', views.booking_stats, name='booking_stats'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
]
