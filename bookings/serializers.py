"""
Serializers for Booking model
"""

from rest_framework import serializers
from .models import Booking
from restaurants.serializers import TablePublicSerializer


class BookingSerializer(serializers.ModelSerializer):
    """
    Full booking serializer - for restaurant owner dashboard
    """
    table_number = serializers.CharField(source='table.table_number', read_only=True)
    table_capacity = serializers.IntegerField(source='table.capacity', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    booking_datetime = serializers.DateTimeField(read_only=True)
    end_datetime = serializers.DateTimeField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    is_today = serializers.BooleanField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'restaurant', 'restaurant_name',
            'table', 'table_number', 'table_capacity',
            'customer_name', 'customer_email', 'customer_phone',
            'party_size', 'booking_date', 'booking_time',
            'booking_datetime', 'end_datetime',
            'duration_hours', 'special_requests',
            'status', 'is_past', 'is_today', 'is_upcoming',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'restaurant', 'created_at', 'updated_at'
        ]


class BookingCreateSerializer(serializers.Serializer):
    """
    Serializer for creating bookings from public booking page
    """
    # Customer info
    customer_name = serializers.CharField(max_length=200)
    customer_email = serializers.EmailField()
    customer_phone = serializers.CharField(max_length=20)

    # Booking details
    table_id = serializers.IntegerField()
    party_size = serializers.IntegerField(min_value=1)
    booking_date = serializers.DateField()
    booking_time = serializers.TimeField()
    duration_hours = serializers.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=2.0,
        min_value=0.5,
        max_value=8.0
    )
    special_requests = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500
    )

    def validate_booking_date(self, value):
        """Ensure booking is not in the past"""
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError("Cannot book in the past")
        return value

    def validate_party_size(self, value):
        """Ensure party size is reasonable"""
        if value > 50:  # Arbitrary max
            raise serializers.ValidationError("Party size too large")
        return value


class AvailabilityCheckSerializer(serializers.Serializer):
    """
    Serializer for checking availability
    """
    booking_date = serializers.DateField()
    booking_time = serializers.TimeField()
    party_size = serializers.IntegerField(min_value=1)
    duration_hours = serializers.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=2.0,
        required=False
    )


class BookingStatsSerializer(serializers.Serializer):
    """
    Serializer for booking statistics on dashboard
    """
    total_bookings = serializers.IntegerField()
    today_bookings = serializers.IntegerField()
    upcoming_bookings = serializers.IntegerField()
    cancelled_bookings = serializers.IntegerField()
    total_revenue_potential = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )

