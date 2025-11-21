from django.shortcuts import render

# Create your views here.
"""
Booking API views
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from restaurants.models import Restaurant, Table
from .models import Booking
from .serializers import (
    BookingSerializer,
    BookingCreateSerializer,
    AvailabilityCheckSerializer,
    BookingStatsSerializer
)
from .services import BookingService


# ==================== PUBLIC BOOKING VIEWS ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def check_availability(request, qr_code_id):
    """
    Check table availability for given date/time
    POST /api/public/<qr_code_id>/availability/
    Body: {
        "booking_date": "2024-12-25",
        "booking_time": "19:00:00",
        "party_size": 4,
        "duration_hours": 2.0
    }
    """
    restaurant = get_object_or_404(Restaurant, qr_code_id=qr_code_id, is_active=True)

    serializer = AvailabilityCheckSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    # Get available tables
    available_tables = BookingService.get_available_tables(
        restaurant=restaurant,
        booking_date=data['booking_date'],
        booking_time=data['booking_time'],
        party_size=data['party_size'],
        duration_hours=data.get('duration_hours', 2.0)
    )

    from restaurants.serializers import TablePublicSerializer
    tables_data = TablePublicSerializer(available_tables, many=True).data

    return Response({
        'available': len(available_tables) > 0,
        'available_tables': tables_data,
        'message': f"{len(available_tables)} tables available" if available_tables else "No tables available for this time slot"
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def create_booking(request, qr_code_id):
    """
    Create a new booking (public endpoint)
    POST /api/public/<qr_code_id>/book/
    Body: {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "customer_phone": "+1234567890",
        "table_id": 1,
        "party_size": 4,
        "booking_date": "2024-12-25",
        "booking_time": "19:00:00",
        "duration_hours": 2.0,
        "special_requests": "Window seat preferred"
    }
    """
    restaurant = get_object_or_404(Restaurant, qr_code_id=qr_code_id, is_active=True)

    serializer = BookingCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    # Extract customer data
    customer_data = {
        'customer_name': data['customer_name'],
        'customer_email': data['customer_email'],
        'customer_phone': data['customer_phone']
    }

    # Extract booking data
    booking_data = {
        'booking_date': data['booking_date'],
        'booking_time': data['booking_time'],
        'party_size': data['party_size'],
        'duration_hours': data.get('duration_hours', 2.0),
        'special_requests': data.get('special_requests', '')
    }

    # Create booking using service
    success, booking, message = BookingService.create_booking(
        restaurant=restaurant,
        table_id=data['table_id'],
        customer_data=customer_data,
        booking_data=booking_data
    )

    if success:
        return Response({
            'message': message,
            'booking': BookingSerializer(booking).data
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'error': message
        }, status=status.HTTP_400_BAD_REQUEST)


# ==================== RESTAURANT DASHBOARD VIEWS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_list(request):
    """
    List all bookings for restaurant owner
    GET /api/bookings/?filter=all|today|upcoming|past|cancelled
    """
    try:
        restaurant = Restaurant.objects.get(owner=request.user)
    except Restaurant.DoesNotExist:
        return Response({
            'error': 'No restaurant found'
        }, status=status.HTTP_404_NOT_FOUND)

    filter_type = request.query_params.get('filter', 'all')

    bookings = BookingService.get_restaurant_bookings(restaurant, filter_type)
    serializer = BookingSerializer(bookings, many=True)

    return Response({
        'filter': filter_type,
        'count': bookings.count(),
        'bookings': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def today_bookings(request):
    """
    Get today's bookings
    GET /api/bookings/today/
    """
    try:
        restaurant = Restaurant.objects.get(owner=request.user)
    except Restaurant.DoesNotExist:
        return Response({
            'error': 'No restaurant found'
        }, status=status.HTTP_404_NOT_FOUND)

    bookings = BookingService.get_restaurant_bookings(restaurant, 'today')
    serializer = BookingSerializer(bookings, many=True)

    return Response({
        'date': timezone.now().date(),
        'count': bookings.count(),
        'bookings': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_stats(request):
    """
    Get booking statistics for dashboard
    GET /api/bookings/stats/
    """
    try:
        restaurant = Restaurant.objects.get(owner=request.user)
    except Restaurant.DoesNotExist:
        return Response({
            'error': 'No restaurant found'
        }, status=status.HTTP_404_NOT_FOUND)

    total_bookings = Booking.objects.filter(restaurant=restaurant).count()
    today_bookings = BookingService.get_restaurant_bookings(restaurant, 'today').count()
    upcoming_bookings = BookingService.get_restaurant_bookings(restaurant, 'upcoming').count()
    cancelled_bookings = BookingService.get_restaurant_bookings(restaurant, 'cancelled').count()

    stats = {
        'total_bookings': total_bookings,
        'today_bookings': today_bookings,
        'upcoming_bookings': upcoming_bookings,
        'cancelled_bookings': cancelled_bookings
    }

    serializer = BookingStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, pk):
    """
    Cancel a booking
    DELETE /api/bookings/<id>/cancel/
    """
    try:
        restaurant = Restaurant.objects.get(owner=request.user)
    except Restaurant.DoesNotExist:
        return Response({
            'error': 'No restaurant found'
        }, status=status.HTTP_404_NOT_FOUND)

    success, message = BookingService.cancel_booking(pk, restaurant)

    if success:
        return Response({
            'message': message
        })
    else:
        return Response({
            'error': message
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_detail(request, pk):
    """
    Get details of a specific booking
    GET /api/bookings/<id>/
    """
    try:
        restaurant = Restaurant.objects.get(owner=request.user)
        booking = Booking.objects.get(pk=pk, restaurant=restaurant)
        serializer = BookingSerializer(booking)
        return Response(serializer.data)
    except Restaurant.DoesNotExist:
        return Response({
            'error': 'No restaurant found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Booking.DoesNotExist:
        return Response({
            'error': 'Booking not found'
        }, status=status.HTTP_404_NOT_FOUND)

