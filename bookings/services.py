"""
Booking business logic and availability checking
This is the CORE of the platform
"""

from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Booking
from restaurants.models import Table


class BookingService:
    """
    Service class to handle all booking-related business logic
    """

    @staticmethod
    def check_table_availability(table, booking_date, booking_time, duration_hours=2.0):
        """
        Check if a table is available for the requested time slot

        Args:
            table: Table instance
            booking_date: Date of booking (date object)
            booking_time: Time of booking (time object)
            duration_hours: Duration of booking in hours

        Returns:
            tuple: (is_available: bool, message: str)
        """
        # Combine date and time
        requested_start = timezone.make_aware(
            datetime.combine(booking_date, booking_time)
        )
        requested_end = requested_start + timedelta(hours=duration_hours)

        # Get all confirmed bookings for this table on this date
        existing_bookings = Booking.objects.filter(
            table=table,
            booking_date=booking_date,
            status='confirmed'
        )

        # Check for overlaps
        for booking in existing_bookings:
            existing_start = booking.booking_datetime
            existing_end = booking.end_datetime

            # Overlap detection formula:
            # Two time ranges overlap if:
            # (start1 < end2) AND (end1 > start2)
            if (existing_start < requested_end) and (existing_end > requested_start):
                return False, f"Table is already booked from {existing_start.strftime('%I:%M %p')} to {existing_end.strftime('%I:%M %p')}"

        return True, "Table is available"

    @staticmethod
    def get_available_tables(restaurant, booking_date, booking_time, party_size, duration_hours=2.0):
        """
        Get all available tables for given criteria

        Args:
            restaurant: Restaurant instance
            booking_date: Date of booking
            booking_time: Time of booking
            party_size: Number of people
            duration_hours: Duration in hours

        Returns:
            QuerySet of available Table objects
        """
        # Get all active tables that can accommodate the party
        suitable_tables = Table.objects.filter(
            restaurant=restaurant,
            is_active=True,
            capacity__gte=party_size
        )

        available_tables = []

        for table in suitable_tables:
            is_available, _ = BookingService.check_table_availability(
                table, booking_date, booking_time, duration_hours
            )
            if is_available:
                available_tables.append(table)

        return available_tables

    @staticmethod
    @transaction.atomic
    def create_booking(restaurant, table_id, customer_data, booking_data):
        """
        Create a new booking with proper validation and race condition prevention

        Args:
            restaurant: Restaurant instance
            table_id: ID of the table
            customer_data: Dict with customer info (name, email, phone)
            booking_data: Dict with booking info (date, time, party_size, duration, special_requests)

        Returns:
            tuple: (success: bool, booking: Booking or None, message: str)
        """
        try:
            # Get table with row-level lock to prevent race conditions
            table = Table.objects.select_for_update().get(
                id=table_id,
                restaurant=restaurant,
                is_active=True
            )

            # Extract booking data
            booking_date = booking_data['booking_date']
            booking_time = booking_data['booking_time']
            party_size = booking_data['party_size']
            duration_hours = booking_data.get('duration_hours', 2.0)

            # Validate party size
            if party_size > table.capacity:
                return False, None, f"Table capacity is {table.capacity}, but party size is {party_size}"

            # Check availability (double-check even with lock)
            is_available, message = BookingService.check_table_availability(
                table, booking_date, booking_time, duration_hours
            )

            if not is_available:
                return False, None, message

            # Validate booking is not in the past
            booking_datetime = timezone.make_aware(
                datetime.combine(booking_date, booking_time)
            )
            if booking_datetime < timezone.now():
                return False, None, "Cannot book in the past"

            # Create the booking
            booking = Booking.objects.create(
                restaurant=restaurant,
                table=table,
                customer_name=customer_data['customer_name'],
                customer_email=customer_data['customer_email'],
                customer_phone=customer_data['customer_phone'],
                party_size=party_size,
                booking_date=booking_date,
                booking_time=booking_time,
                duration_hours=duration_hours,
                special_requests=booking_data.get('special_requests', ''),
                status='confirmed'
            )

            return True, booking, "Booking confirmed successfully"

        except Table.DoesNotExist:
            return False, None, "Table not found or not available"
        except Exception as e:
            return False, None, f"Error creating booking: {str(e)}"

    @staticmethod
    def cancel_booking(booking_id, restaurant):
        """
        Cancel a booking

        Args:
            booking_id: ID of booking to cancel
            restaurant: Restaurant instance (for authorization)

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            booking = Booking.objects.get(
                id=booking_id,
                restaurant=restaurant
            )

            if booking.cancel():
                return True, "Booking cancelled successfully"
            else:
                return False, "Booking cannot be cancelled"

        except Booking.DoesNotExist:
            return False, "Booking not found"

    @staticmethod
    def get_restaurant_bookings(restaurant, filter_type='all'):
        """
        Get bookings for a restaurant with filters

        Args:
            restaurant: Restaurant instance
            filter_type: 'all', 'today', 'upcoming', 'past', 'cancelled'

        Returns:
            QuerySet of Booking objects
        """
        base_query = Booking.objects.filter(restaurant=restaurant)

        today = timezone.now().date()
        now = timezone.now()

        if filter_type == 'today':
            return base_query.filter(booking_date=today, status='confirmed')

        elif filter_type == 'upcoming':
            return base_query.filter(
                booking_date__gte=today,
                status='confirmed'
            ).exclude(booking_date=today, booking_time__lt=now.time())

        elif filter_type == 'past':
            return base_query.filter(
                booking_date__lt=today
            ) | base_query.filter(
                booking_date=today,
                booking_time__lt=now.time()
            )

        elif filter_type == 'cancelled':
            return base_query.filter(status='cancelled')

        else:  # 'all'
            return base_query
