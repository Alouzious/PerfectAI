from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from .models import UserProfile
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login user"""
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Update last login in profile
            if hasattr(user, 'profile'):
                from django.utils import timezone
                user.profile.last_login_at = timezone.now()
                user.profile.save()
            
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout user"""
    logout(request)
    return Response({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """Get current logged-in user"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """Get or update user profile"""
    profile = request.user.profile
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for monitoring"""
    return Response({
        'status': 'healthy',
        'service': 'Pitch Perfect API',
        'version': '1.0.0'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """Request password reset email"""
    email = request.data.get('email')
    
    try:
        user = User.objects.get(email=email)
        # TODO: Send password reset email
        return Response({
            'message': 'If that email exists, password reset instructions have been sent.'
        })
    except User.DoesNotExist:
        return Response({
            'message': 'If that email exists, password reset instructions have been sent.'
        })


@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token_view(request):
    """Get CSRF token - call this before any POST requests"""
    return Response({'csrfToken': get_token(request)})