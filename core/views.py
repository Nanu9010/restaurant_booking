from django.shortcuts import render

# Create your views here.
"""
Core authentication views
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.shortcuts import render
from .serializers import SignupSerializer, LoginSerializer, UserSerializer


# ==================== PAGE VIEWS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def login_page(request):
    """Render login page"""
    return render(request, 'auth/login.html')


@api_view(['GET'])
@permission_classes([AllowAny])
def signup_page(request):
    """Render signup page"""
    return render(request, 'auth/signup.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def owner_dashboard_page(request):
    """Render owner dashboard page"""
    # Check if user is owner
    if not request.user.profile.is_owner:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    return render(request, 'dashboards/owner_dashboard.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_page(request):
    """Render admin dashboard page"""
    # Check if user is admin
    if not request.user.profile.is_admin:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    return render(request, 'dashboards/admin_dashboard.html')


# ==================== API ENDPOINTS ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    Signup endpoint for both Admin and Owner
    POST /api/auth/signup/
    """
    serializer = SignupSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        # Create auth token
        token, _ = Token.objects.get_or_create(user=user)

        # Get user data with profile
        user_serializer = UserSerializer(user)

        return Response({
            'message': 'Registration successful',
            'token': token.key,
            'user': user_serializer.data,
            'redirect_url': user.profile.dashboard_url
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login endpoint
    POST /api/auth/login/
    """
    serializer = LoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    user = authenticate(username=username, password=password)

    if user:
        token, _ = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user)

        return Response({
            'message': 'Login successful',
            'token': token.key,
            'user': user_serializer.data,
            'redirect_url': user.profile.dashboard_url
        })

    return Response({
        'error': 'Invalid credentials'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout endpoint
    POST /api/auth/logout/
    """
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logout successful'})
    except:
        return Response({
            'error': 'Logout failed'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Get current logged-in user info
    GET /api/auth/me/
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
