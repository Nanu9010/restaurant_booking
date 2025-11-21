from django.contrib import admin

# Register your models here.
"""
Django Admin configuration for Restaurant and Table models
"""

from django.contrib import admin
from .models import Restaurant, Table


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    """Admin interface for Restaurant model"""

    list_display = [
        'name', 'owner_username', 'city', 'phone',
        'is_active', 'created_at'
    ]

    list_filter = ['is_active', 'city', 'state', 'created_at']

    search_fields = ['name', 'owner__username', 'email', 'phone', 'address']

    readonly_fields = ['qr_code_id', 'booking_url', 'qr_code_url', 'created_at', 'updated_at']

    fieldsets = (
        ('Owner Information', {
            'fields': ('owner',)
        }),
        ('Restaurant Details', {
            'fields': ('name', 'description', 'email', 'phone')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'zip_code')
        }),
        ('Images', {
            'fields': ('logo', 'cover_image')
        }),
        ('Operating Hours', {
            'fields': ('opening_time', 'closing_time')
        }),
        ('QR Code & Booking', {
            'fields': ('qr_code_id', 'booking_url', 'qr_code_url')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def owner_username(self, obj):
        return obj.owner.username

    owner_username.short_description = 'Owner'
    owner_username.admin_order_field = 'owner__username'


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    """Admin interface for Table model"""

    list_display = [
        'table_number', 'restaurant_name', 'capacity',
        'is_active', 'created_at'
    ]

    list_filter = ['is_active', 'restaurant', 'capacity', 'created_at']

    search_fields = ['table_number', 'restaurant__name', 'description']

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Table Information', {
            'fields': ('restaurant', 'table_number', 'capacity', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def restaurant_name(self, obj):
        return obj.restaurant.name

    restaurant_name.short_description = 'Restaurant'
    restaurant_name.admin_order_field = 'restaurant__name'
