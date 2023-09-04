from django import forms 
from django.conf import settings
from django.core import validators
from django.contrib import auth as dj_auth
from django.contrib.auth import password_validation, get_user_model
from django.contrib.auth.models import update_last_login
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError


from hashid_field import rest
from rest_framework import serializers

from common.decorators import context_user_required

from .services import otp as otp_services
from .utils import generate_otp_auth_token
from .models import User, UserProfile, UserAvatar
from . import notifications, models, tokens

UPLOADED_AVATAR_SIZE_LIMIT = 1 * 1024 * 1024


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"autocorrect": "off", "autocapitalize": "off"}),
    )
    password = forms.CharField(required=True, widget=forms.PasswordInput())


class UserProfileForm(forms.ModelForm):
    # email = forms.EmailField()
    avatar = forms.FileField(required=False)

    class Meta:
        model = UserProfile
        fields = ("first_name", "last_name", "avatar")

    @staticmethod
    def clean_avatar(avatar):
        if avatar and avatar.size > UPLOADED_AVATAR_SIZE_LIMIT:
            raise ValidationError({"avatar": _("Too large file")}, 'too_large')
        return avatar

    def to_representation(self, user):
        self.fields["avatar"] = forms.FileField(source="avatar.thumbnail", default="")
        return super().to_representation(user)

    def update(self, user):
        avatar = self.cleaned_data.pop("avatar", None)
        # email = self.cleaned_data.pop("email")
        if avatar:
            if not user.avatar:
                user.avatar = UserAvatar()
            user.avatar.original = avatar
            user.avatar.save()
        # if email:
        #     if not user.user:
        #         user.user = User()
        #     user.user.email = email
        #     user.user.save()
        return super().update(user)


class UserSignupForm(forms.ModelForm):
    email = forms.EmailField(
        validators=[validators.EmailValidator()],
    )
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(render_value=True))
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(render_value=True))

    class Meta:
        model = dj_auth.get_user_model()
        fields = ("email", "password1", "password2",)

    def clean_password1(self):
        password = self.cleaned_data["password1"]
        password_validation.validate_password(password)
        return password
    
    def clean_password2(self):
        password = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]
        if password and password2 and password != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = dj_auth.get_user_model().objects.create_user(
            self.cleaned_data["email"],
            self.cleaned_data["password2"],
        )

        # if jwt_api_settings.UPDATE_LAST_LOGIN:
        #     update_last_login(None, user)
        
        if commit:
            user.save()
        
        notifications.AccountActivationEmail(
            user=user, 
            data={
                'user_id': user.id.hashid, 
                'token': tokens.account_activation_token.make_token(user)}
        ).send()
        return user


class UserAccountConfirmationForm(forms.Form):
    user = serializers.PrimaryKeyRelatedField(
        queryset=models.User.objects.all(),
        pk_field=rest.HashidSerializerCharField()
    )
    token = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()
        token = cleaned_data["token"]
        user = cleaned_data["user"]

        if not tokens.account_activation_token.check_token(user, token):
            raise exceptions.ValidationError(_("Malformed user account confirmation token"))
        return cleaned_data

    def save(self, commit=True):
        user = cleaned_data.pop("user")
        user.is_confirmed = True
        if commit:
            user.save()
        return user


class UserAccountResendConfirmationForm(forms.Form):
    email = forms.EmailField(help_text=_("User e-mail"))
    
    def clean(self):
        cleaned_data = super().clean()
        user = None
        email = cleaned_data["email"]
        try:
            user = dj_auth.get_user_model().objects.get(email=email)
        except dj_auth.get_user_model().DoesNotExist:
            pass
        return {**cleaned_data, 'user': user}
        
    def save(self, commit=True):
        user = self.cleaned_data.pop('user')
        
        if user:
        #     if jwt_api_settings.UPDATE_LAST_LOGIN:
        #         update_last_login(None, user)
            
            notifications.AccountActivationEmail(
                user=user, 
                data={
                    'user_id': user.id.hashid, 
                    'token': tokens.account_activation_token.make_token(user)
                }
            ).send()
        return user


class UserAccountChangePasswordForm(forms.Form):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    old_password = forms.CharField(label="Old Password", widget=forms.PasswordInput(render_value=True))
    new_password = forms.CharField(label="New Password", widget=forms.PasswordInput(render_value=True))
    re_new_password = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput(render_value=True))

    def clean_new_password(self):
        new_password = self.cleaned_data["new_password"]
        password_validation.validate_password(new_password)
        return new_password
    
    def clean_re_new_password(self):
        new_password = self.cleaned_data["new_password"]
        re_new_password = self.cleaned_data["re_new_password"]
        if not new_password == re_new_password:
            raise ValidationError({"re_new_password": _("Password not match!")}, 'not_match_password')
        return re_new_password

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data["old_password"]
        new_password = cleaned_data["new_password"]
        re_new_password = cleaned_data["re_new_password"]
        
        user = cleaned_data["user"]
        if not user.check_password(old_password):
            raise ValidationError({"old_password": _("Wrong old password")}, 'wrong_password')
        return cleaned_data

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        user = cleaned_data.pop("user")
        new_password = cleaned_data.pop("new_password")
        user.set_password(new_password)
        if commit:
            user.save()
        return user


class PasswordResetForm(forms.Form):
    email = forms.EmailField(help_text=_("User e-mail"))

    def clean(self):
        cleaned_data = super().clean()
        user = None
        try:
            user = dj_auth.get_user_model().objects.get(email=cleaned_data["email"])
        except dj_auth.get_user_model().DoesNotExist:
            pass

        return {**cleaned_data, 'user': user}

    def save(self, commit=True):
        user = self.cleaned_data.pop('user')
        if user:
            notifications.PasswordResetEmail(
                user=user, 
                data={
                    'user_id': user.id.hashid, 
                    'token': tokens.password_reset_token.make_token(user)}
            ).send()
        return user


class PasswordResetConfirmationForm(forms.Form):
    # user field is a CharField by design to hide the information whether the user exists or not
    user = forms.CharField(widget=forms.HiddenInput())
    new_password = forms.CharField(label="New Password", widget=forms.PasswordInput(render_value=True))
    re_new_password = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput(render_value=True))
    token = forms.CharField(widget=forms.HiddenInput())
    
    def clean_new_password(self):
        new_password = self.cleaned_data["new_password"]
        password_validation.validate_password(new_password)
        return new_password

    def clean(self):
        attrs = super().clean()
        token = attrs["token"]
        user_id = attrs["user"]
        new_password = attrs["new_password"]
        re_new_password = attrs["re_new_password"]
        
        try:
            user = models.User.objects.get(pk=user_id)
        except models.User.DoesNotExist:
            raise exceptions.ValidationError(_("Malformed password reset token"), 'invalid_token')
        
        if not tokens.password_reset_token.check_token(user, token):
            raise exceptions.ValidationError(_("Malformed password reset token"), 'invalid_token')
        
        if not new_password == re_new_password:
            raise exceptions.ValidationError({"re_new_password": _("Password not match!")}, 'not_match_password')
        return {**attrs, 'user': user}

    def save(self, commit=True):
        user = self.cleaned_data.pop("user")
        new_password = self.cleaned_data.pop("new_password")
        user.set_password(new_password)
        jwt.blacklist_user_tokens(user)
        if commit:
            user.save()
        return user


@context_user_required
class VerifyOTPForm(forms.Form):
    otp_token = forms.CharField()

    def save(self):
        otp_services.verify_otp(self.context_user, self.cleaned_data.get("otp_token", ""))
        return True


class ValidateOTPForm(forms.Form):
    user_id = forms.CharField(widget=forms.HiddenInput())
    otp_token = forms.CharField()
    
    def clean(self):
        cleaned_data = super().clean()
        try:
            user = User.objects.get(id=cleaned_data["user_id"])
        except:
            pass 
        return {"user": user, **cleaned_data}
    
    def validate(self):
        user = self.cleaned_data["user"]
        otp_token = self.cleaned_data["otp_token"]
        
        otp_services.validate_otp(user, otp_token)