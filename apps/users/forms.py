from django import forms 
from django.conf import settings
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


class UserProfileForm(forms.ModelForm):
    id = rest.HashidSerializerCharField(source_field="users.User.id", source="user.id", read_only=True)
    email = forms.CharField(source="user.email", read_only=True)
    avatar = forms.FileField(required=False)

    class Meta:
        model = UserProfile
        fields = ("id", "first_name", "last_name", "email", "avatar")

    @staticmethod
    def clean_avatar(avatar):
        if avatar and avatar.size > UPLOADED_AVATAR_SIZE_LIMIT:
            raise ValidationError({"avatar": _("Too large file")}, 'too_large')
        return avatar

    def to_representation(self, instance):
        self.fields["avatar"] = forms.FileField(source="avatar.thumbnail", default="")
        return super().to_representation(instance)

    def update(self, instance, self.cleaned_data):
        avatar = self.cleaned_data.pop("avatar", None)
        if avatar:
            if not instance.avatar:
                instance.avatar = UserAvatar()
            instance.avatar.original = avatar
            instance.avatar.save()
        return super().update(instance, self.cleaned_data)


class UserSignupForm(forms.ModelForm):
    email = forms.EmailField(
        validators=[validators.UniqueValidator(queryset=dj_auth.get_user_model().objects.all())],
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

    def validate(self):
        token = self.cleaned_data["token"]
        user = self.cleaned_data["user"]

        if not tokens.account_activation_token.check_token(user, token):
            raise exceptions.ValidationError(_("Malformed user account confirmation token"))

        return self.cleaned_data

    def save(self, commit=True):
        user = cleaned_data.pop("user")
        user.is_confirmed = True
        if commit:
            user.save()
        return user
        