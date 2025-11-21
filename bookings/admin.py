from django.contrib import admin

# Register your models here.
"""
Django Admin configuration for Booking model
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin interface for Booking model"""

    list_display = [
        'id', 'customer_name', 'restaurant_name', 'table_display',
        'booking_date', 'booking_time', 'party_size',
        'status_badge', 'created_at'
    ]

    list_filter = [
        'status', 'booking_date', 'restaurant',
        'table', 'created_at'
    ]

    search_fields = [
        'customer_name', 'customer_email', 'customer_phone',
        'restaurant__name', 'table__table_number'
    ]

    readonly_fields = [
        'booking_datetime', 'end_datetime',
        'is_past', 'is_today', 'is_upcoming',
        'created_at', 'updated_at'
    ]

    date_hierarchy = 'booking_date'

    fieldsets = (
        ('Booking Information', {
            'fields': ('restaurant', 'table', 'status')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Booking Details', {
            'fields': (
                'party_size', 'booking_date', 'booking_time',
                'duration_hours', 'special_requests'
            )
        }),
        ('Computed Fields', {
            'fields': (
                'booking_datetime', 'end_datetime',
                'is_past', 'is_today', 'is_upcoming'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_cancelled', 'mark_as_completed', 'mark_as_no_show']

    def restaurant_name(self, obj):
        return obj.restaurant.name

    restaurant_name.short_description = 'Restaurant'
    restaurant_name.admin_order_field = 'restaurant__name'

    def table_display(self, obj):
        return f"Table {obj.table.table_number}"

    table_display.short_description = 'Table'
    table_display.admin_order_field = 'table__table_number'

    def status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'confirmed': 'green',
            'cancelled': 'red',
            'completed': 'blue',
            'no_show': 'orange'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_badge.short_description = 'Status'

    # Admin actions
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} bookings marked as cancelled.')

    mark_as_cancelled.short_description = 'Mark selected bookings as Cancelled'

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} bookings marked as completed.')

    mark_as_completed.short_description = 'Mark selected bookings as Completed'

    def mark_as_no_show(self, request, queryset):
        updated = queryset.update(status='no_show')
        self.message_user(request, f'{updated} bookings marked as no show.')

    mark_as_no_show.short_description = 'Mark selected bookings as No Show'

