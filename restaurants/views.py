from django.shortcuts import render

# Create your views here.
"""
Restaurant and Table API views
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Restaurant, Table
from .serializers import (
    UserRegistrationSerializer,
    RestaurantSerializer,
    RestaurantPublicSerializer,
    TableSerializer,
    TablePublicSerializer
)
from core.utils import generate_restaurant_qr
import base64


# ==================== AUTHENTICATION VIEWS ====================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_restaurant(request):
    """
    Register a new restaurant owner
    POST /api/auth/signup/
    """
    serializer = UserRegistrationSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        # Create auth token
        token, _ = Token.objects.get_or_create(user=user)

        # Get created restaurant
        restaurant = Restaurant.objects.get(owner=user)

        return Response({
            'message': 'Registration successful',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'restaurant': RestaurantSerializer(restaurant).data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_restaurant(request):
    """
    Login restaurant owner
    POST /api/auth/login/
    Body: {"username": "...", "password": "..."}
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({
            'error': 'Username and password required'
        }, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user:
        token, _ = Token.objects.get_or_create(user=user)

        # Get restaurant
        try:
            restaurant = Restaurant.objects.get(owner=user)
            return Response({
                'message': 'Login successful',
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                'restaurant': RestaurantSerializer(restaurant).data
            })
        except Restaurant.DoesNotExist:
            return Response({
                'error': 'No restaurant associated with this account'
            }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'error': 'Invalid credentials'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_restaurant(request):
    """
    Logout restaurant owner (delete token)
    POST /api/auth/logout/
    """
    try:
        request.user.auth_token.delete()
        return Response({
            'message': 'Logout successful'
        })
    except:
        return Response({
            'error': 'Logout failed'
        }, status=status.HTTP_400_BAD_REQUEST)


# ==================== RESTAURANT PROFILE VIEWS ====================

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def restaurant_profile(request):
    """
    Get or update restaurant profile
    GET/PUT/PATCH /api/restaurants/profile/
    """
    try:
        restaurant = Restaurant.objects.get(owner=request.user)
    except Restaurant.DoesNotExist:
        return Response({
            'error': 'No restaurant found for this user'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = RestaurantSerializer(
            restaurant,
            data=request.data,
            partial=partial
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Restaurant updated successfully',
                'data': serializer.data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def restaurant_qr_code(request):
    """
    Get QR code for restaurant
    GET /api/restaurants/qr/
    """
    try:
        restaurant = Restaurant.objects.get(owner=request.user)
        qr_base64 = generate_restaurant_qr(restaurant)

        return Response({
            'qr_code': qr_base64,
            'booking_url': restaurant.booking_url,
            'qr_code_id': str(restaurant.qr_code_id)
        })
    except Restaurant.DoesNotExist:
        return Response({
            'error': 'Restaurant not found'
        }, status=status.HTTP_404_NOT_FOUND)


# ==================== TABLE MANAGEMENT VIEWS ====================

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def table_list_create(request):
    """
    List all tables or create new table
    GET/POST /api/tables/
    """
    try:
        restaurant = Restaurant.objects.get(owner=request.user)
    except Restaurant.DoesNotExist:
        return Response({
            'error': 'No restaurant found'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        tables = Table.objects.filter(restaurant=restaurant)
        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TableSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(restaurant=restaurant)
            return Response({
                'message': 'Table created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def table_detail(request, pk):
    """
    Get, update, or delete a specific table
    GET/PUT/PATCH/DELETE /api/tables/<id>/
    """
    try:
        restaurant = Restaurant.objects.get(owner=request.user)
        table = Table.objects.get(pk=pk, restaurant=restaurant)
    except (Restaurant.DoesNotExist, Table.DoesNotExist):
        return Response({
            'error': 'Table not found'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TableSerializer(table)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = TableSerializer(table, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Table updated successfully',
                'data': serializer.data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        table.delete()
        return Response({
            'message': 'Table deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


# ==================== PUBLIC VIEWS (NO AUTH) ====================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_restaurant_info(request, qr_code_id):
    """
    Get public restaurant information for booking page
    GET /api/public/<qr_code_id>/info/
    """
    restaurant = get_object_or_404(Restaurant, qr_code_id=qr_code_id, is_active=True)
    serializer = RestaurantPublicSerializer(restaurant)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_restaurant_tables(request, qr_code_id):
    """
    Get all active tables for a restaurant
    GET /api/public/<qr_code_id>/tables/
    """
    restaurant = get_object_or_404(Restaurant, qr_code_id=qr_code_id, is_active=True)
    tables = Table.objects.filter(restaurant=restaurant, is_active=True)
    serializer = TablePublicSerializer(tables, many=True)
    return Response(serializer.data)









