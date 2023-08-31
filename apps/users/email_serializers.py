from rest_framework import serializers

class CustomMailSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    subject = serializers.CharField()
    message = serializers.CharField()


class AccountActivationEmailSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    token = serializers.CharField()


class PasswordResetEmailSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    token = serializers.CharField()
    