from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView, UpdateView

from . import notifications, forms

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
class LoginView(FormView):
    form_class = forms.UserLoginForm
    template_name = "users/login.html" 
    success_url = reverse_lazy("users:profile") 
    
    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        
    def form_valid(self, form):
        password = form.cleaned_data["password"]
        email = form.cleaned_data["email"]
        
        user = authenticate(username=email, password=password)
        
        if user is not None:
            if user.is_active:
                if user.otp_enabled and user.otp_verified:
                    notifications.OTPAuthMail(user, {"user_id": user.id.hash, "otp_token": str(generate_otp_auth_token(self.user))})
                    messages.info(self.request, "Check your email for otp")
                else
                    login(self.request, user)
                    messages.info(self.request, "Login successful!")
            else:
                messages.info(self.request, "Check your emial to activate your account!")
        return super().form_valid()


class LogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return render(request, "users/login.html")


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        profile = UserProfile.objects.prefetch_related("user", "avatar").get(user=request.user)
        context = {
            "profile": profile, 
            "update_form": forms.UserProfileForm,
            "password_change_form": forms.UserAccountChangePasswordForm,
        }
        return render(request, "users/profile.html", context)
    
    def post(self, request, *args, **kwargs):
        profile = UserProfile.objects.prefetch_related("user", "avatar").get(user=request.user)
        profile_data = {
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            # "email": request.user.email,
            "avatar": profile.avatar,
        }
        
        update_form = forms.UserProfileForm(request.POST, initial=profile_data)
        if update_form.has_changed():
            if update_form.is_valid():
                update_form.update(profile)
                messages.success(self.request, "Profile update successful!")
            else:
                for error in update_form.errors:
                    messages.error(self.request, error)
        
        context = {
            "profile": profile, 
            "update_form": update_form,
            "password_change_form": forms.UserAccountChangePasswordForm,
        }
        
        if request.POST.get("new_password") != "":
            password_change_form = forms.UserAccountChangePasswordForm(request.POST)
            if password_change_form.is_valid():
                password_change_form.save()
                messages.success(self.request, "Password change successful!")
            else:
                for error in password_change_form.errors:
                    messages.error(self.request, error)
            context["password_change_form"] = password_change_form
        return render(request, "users/profile.html", context)


class SignUpView(FormView):
    form_class = forms.UserSignupForm
    template_name = "users/signup.html" 
    success_url = reverse_lazy("users:signup_confirm") 
    
    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        
    def form_valid(self, form):
        form.save()
        return super().form_valid()


class AccountConfirmationView(View):
    def post(self, request, user, token, *args, **kwargs):
        form = forms.UserAccountConfirmationForm(data={"user": user, "token": token})
        if form.is_valid():
            form.save()
            return render(request, "users/login.html")
        for error in form.errors:
            messages.error(request, error)
        return render(request, "users/signup_confirm.html")


class UserAccountResendConfirmationView(FormView):
    form_class = forms.UserAccountResendConfirmationForm
    template_name = "users/confirmation_resend.html" 
    success_url = reverse_lazy("users:signup_confirm") 
    
    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            for error in form.errors:
                messages.error(request, error)
            return self.form_invalid(form)
        
    def form_valid(self, form):
        form.save()
        return super().form_valid()
    

class PasswordResetView(FormView):
    form_class = forms.PasswordResetForm
    template_name = "users/password_reset.html" 
    success_url = reverse_lazy("users:password_reset_confirm") 
    
    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            for error in form.errors:
                messages.error(request, error)
            return self.form_invalid(form)
        
    def form_valid(self, form):
        form.save()
        return super().form_valid()


class PasswordResetConfirmationView(View):
    
    def post(self, request, user, token, *args, **kwargs):
        initial = {
            "user": user,
            "token": token,
            "new_password": "",
            "re_new_password": "",
        }
        form = forms.PasswordResetConfirmationForm(request.POST, initial=initial)
        if form.has_changed():
            if form.is_valid():
                form.save()
                messages.success(request, "Password reset successful!")
                return render(request, "users/login.html")
            for error in form.errors:
                messages.error(request, error)
        return render(request, "users/password_reset_confirm.html", {"form": form})
        
        
        
