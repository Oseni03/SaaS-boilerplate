from django.urls import path, re_path

from . import views

app_name = "users"

urlpatterns = [
    re_path("^o/(?P<provider>\s+)/$", views.CustomProvideAuthView.as_view(), name="provider-auth"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("activation/{user}/{token}/", views.AccountConfirmationView.as_view(), name="activation"),
    path("activation/resend/", views.UserAccountResendConfirmationView.as_view(), name="activation_resend"),
    path("password-reset/", views.PasswordResetView.as_view(), name="password_reset"),
    # path("password-reset/{user}/{token}/", views.PasswordResetConfirmationView.as_view(), name="password_reset_confirm"),
    path("password-reset/{user}/{token}/", views.password_reset_confirm, name="password_reset_confirm"),
    
    ## OTP URLS
    path("generate-otp/", views.GenerateOTP.as_view(), name="generate_OTP"),
    path("disable-otp/", views.disableOTP, name="disable_OTP"),
]