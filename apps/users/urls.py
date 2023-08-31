from django.urls import path, re_path

from .views import (
    CustomProvideAuthView,
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView, MeView,
    LogoutView, UserCreateView,
    AccountConfirmationView,
    UserAccountResendConfirmationView,
    UserAccountChangePasswordView,
    PasswordResetView, 
    PasswordResetConfirmationView
)

urlpatterns = [
    re_path("^o/(?P<provider>\s+)/$", CustomProvideAuthView.as_view(), name="provider-auth"),
    path("jwt/create", TokenObtainPairView.as_view()),
    path("jwt/refresh", TokenRefreshView.as_view()),
    path("jwt/verify", TokenVerifyView.as_view()),
    path("auth/logout", LogoutView.as_view()),
    path("me/", MeView.as_view()),
    path("activation/{user}/{token}/", AccountConfirmationView.as_view()),
    path("activation-resend/", UserAccountResendConfirmationView.as_view()),
    path("set_password/", UserAccountChangePasswordView.as_view()),
    path("password-reset/", PasswordResetView.as_view()),
    path("password-reset/{user}/{token}/", PasswordResetConfirmationView.as_view()),
    path("", UserCreateView.as_view()),
]