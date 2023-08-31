from django.conf import settings
from django.contrib.auth import get_user_model

from djoser.social.views import ProviderAuthView
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework import status

from rest_framework_simplejwt import views as jwt_views

from .serializers import (
    UserProfileSerializer, PasswordResetSerializer,
    UserAccountConfirmationSerializer,
    UserAccountChangePasswordSerializer,
    UserSignupSerializer,
    UserAccountResendConfirmationSerializer,
    PasswordResetConfirmationSerializer,
    LogoutSerializer, 
    CookieTokenRefreshSerializer,
    CookieTokenObtainPairSerializer
)


class CustomProvideAuthView(ProviderAuthView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            access_token = response.data.get("access")
            refresh_token = response.data.get("refresh")
            
            response.set_cookie(
                "access", access_token,
                max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
            
            response.set_cookie(
                "refresh", refresh_token,
                max_age=settings.AUTH_COOKIE_REFRESH_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
        return response


# Create your views here.
class TokenObtainPairView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CookieTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CookieTokenRefreshSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenVerifyView(jwt_views.TokenVerifyView):
    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access')
        
        if access_token:
            request.data["token"] = access_token
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    def get(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(data=request.user.profile, many=False)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        user = request.user 
        user.is_active=False 
        user.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class UserCreateView(mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSignupSerializer
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AccountConfirmationView(APIView):
    def post(self, request, user, token, *args, **kwargs):
        serializer = UserAccountConfirmationSerializer(data={"user": user, "token": token})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAccountResendConfirmationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserAccountResendConfirmationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserAccountChangePasswordView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserAccountChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmationView(APIView):
    def post(self, request, user, token, *args, **kwargs):
        serializer = PasswordResetConfirmationSerializer(data={"user": user, "token": token})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
