"""
Main URL configuration for restaurant booking platform
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Core app (Auth & Dashboards)
    path('', include('core.urls')),

    # Restaurants app
    path('', include('restaurants.urls')),

    # Bookings app
    path('', include('bookings.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)