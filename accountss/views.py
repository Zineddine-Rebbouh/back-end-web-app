from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
import logging

logger = logging.getLogger(__name__)

class SignupView(APIView):
    def post(self, request):
        logger.info(f"Signup attempt with data: {request.data}")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            logger.info(f"User created: {user.username}")
            return Response({
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)
        logger.error(f"Signup failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        logger.info(f"Login attempt with email: {email}")
        logger.info(f"Login attempt with password: {password}")
        
        user = authenticate(email=email, password=password)
        if user:
            logger.info(f"User authenticated: {user.username}")
            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
        logger.error("Authentication failed: Invalid credentials")
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)