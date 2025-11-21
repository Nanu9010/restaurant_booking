"""
Serializers for Restaurant and Table models
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Restaurant, Table


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']


class RestaurantSerializer(serializers.ModelSerializer):
    """
    Full serializer for Restaurant with all fields
    Used for owner's own restaurant management
    """
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    booking_url = serializers.CharField(read_only=True)
    qr_code_url = serializers.CharField(read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            'id', 'owner', 'owner_username', 'owner_email',
            'name', 'description', 'email', 'phone',
            'address', 'city', 'state', 'zip_code',
            'logo', 'cover_image',
            'qr_code_id', 'booking_url', 'qr_code_url',
            'opening_time', 'closing_time',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'qr_code_id', 'created_at', 'updated_at']


class RestaurantPublicSerializer(serializers.ModelSerializer):
    """
    Public serializer - only shows info needed for booking page
    Hides sensitive owner information
    """

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'description',
            'address', 'city', 'state',
            'logo', 'cover_image',
            'opening_time', 'closing_time'
        ]


class TableSerializer(serializers.ModelSerializer):
    """Serializer for Table model"""
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = Table
        fields = [
            'id', 'restaurant', 'restaurant_name',
            'table_number', 'capacity', 'description',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'restaurant', 'created_at', 'updated_at']

    def validate_capacity(self, value):
        """Ensure capacity is positive"""
        if value < 1:
            raise serializers.ValidationError("Capacity must be at least 1")
        return value


class TablePublicSerializer(serializers.ModelSerializer):
    """
    Public table serializer - for booking page
    Shows only necessary information
    """

    class Meta:
        model = Table
        fields = ['id', 'table_number', 'capacity', 'description']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for restaurant owner registration
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    # Restaurant details
    restaurant_name = serializers.CharField(write_only=True)
    restaurant_email = serializers.EmailField(write_only=True)
    restaurant_phone = serializers.CharField(write_only=True)
    restaurant_address = serializers.CharField(write_only=True)
    restaurant_city = serializers.CharField(write_only=True)
    restaurant_state = serializers.CharField(write_only=True)
    restaurant_zip = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'restaurant_name', 'restaurant_email', 'restaurant_phone',
            'restaurant_address', 'restaurant_city', 'restaurant_state',
            'restaurant_zip'
        ]

    def validate(self, data):
        """Validate passwords match"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        """Create user and restaurant together"""
        
        # Extract restaurant data
        restaurant_data = {
            'name': validated_data.pop('restaurant_name'),
            'email': validated_data.pop('restaurant_email'),
            'phone': validated_data.pop('restaurant_phone'),
            'address': validated_data.pop('restaurant_address'),
            'city': validated_data.pop('restaurant_city'),
            'state': validated_data.pop('restaurant_state'),
            'zip_code': validated_data.pop('restaurant_zip'),
        }

        # Remove password_confirm
        validated_data.pop('password_confirm')

        # Create user
        user = User.objects.create_user(**validated_data)

        # Create restaurant
        Restaurant.objects.create(owner=user, **restaurant_data)

        return user
