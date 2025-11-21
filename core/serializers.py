"""
Core serializers for authentication
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
from restaurants.models import Restaurant


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile"""

    class Meta:
        model = UserProfile
        fields = ['role', 'phone', 'avatar', 'is_admin', 'is_owner', 'dashboard_url']
        read_only_fields = ['is_admin', 'is_owner', 'dashboard_url']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User with profile"""
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']


class SignupSerializer(serializers.Serializer):
    """
    Unified signup serializer for both Admin and Owner
    """
    # User credentials
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)

    # Role selection
    role = serializers.ChoiceField(choices=['admin', 'owner'])

    # Profile info
    phone = serializers.CharField(max_length=20, required=False)

    # Restaurant info (required only for owners)
    restaurant_name = serializers.CharField(required=False)
    restaurant_email = serializers.EmailField(required=False)
    restaurant_phone = serializers.CharField(required=False)
    restaurant_address = serializers.CharField(required=False)
    restaurant_city = serializers.CharField(required=False)
    restaurant_state = serializers.CharField(required=False)
    restaurant_zip = serializers.CharField(required=False)

    def validate(self, data):
        """Validate passwords match and role-specific requirements"""
        # Check passwords match
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")

        # Check username is unique
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists")

        # Check email is unique
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists")

        # If owner, require restaurant details
        if data['role'] == 'owner':
            required_fields = [
                'restaurant_name', 'restaurant_email', 'restaurant_phone',
                'restaurant_address', 'restaurant_city', 'restaurant_state', 'restaurant_zip'
            ]
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError(f"{field} is required for restaurant owners")

        return data

    def create(self, validated_data):
        """Create user with appropriate role"""
        # Remove password_confirm and extract data
        validated_data.pop('password_confirm')
        role = validated_data.pop('role')
        phone = validated_data.pop('phone', '')

        # Extract restaurant data if owner
        restaurant_data = {}
        if role == 'owner':
            restaurant_data = {
                'name': validated_data.pop('restaurant_name'),
                'email': validated_data.pop('restaurant_email'),
                'phone': validated_data.pop('restaurant_phone'),
                'address': validated_data.pop('restaurant_address'),
                'city': validated_data.pop('restaurant_city'),
                'state': validated_data.pop('restaurant_state'),
                'zip_code': validated_data.pop('restaurant_zip'),
            }

        # Create user
        user = User.objects.create_user(**validated_data)

        # Update profile with role
        profile = user.profile
        profile.role = role
        profile.phone = phone
        profile.save()

        # Create restaurant if owner
        if role == 'owner' and restaurant_data:
            Restaurant.objects.create(owner=user, **restaurant_data)

        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
