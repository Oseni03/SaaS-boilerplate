from rest_framework import serializers

class OTPAuthSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    otp_token = serializers.CharField()


class AccountActivationEmailSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    token = serializers.CharField()


class PasswordResetEmailSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    token = serializers.CharField()
    