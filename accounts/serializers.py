from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name',
            'password', ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        instance = User.objects.create(**validated_data)
        instance.set_password(password)
        instance.save()
        return instance
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Get the email and password from the submitted data
        email = attrs.get('email')
        password = attrs.get('password')

        # Perform your custom validation logic
        # Here, you can use Django's authentication system to authenticate the user using email and password
        # For example:
        from django.contrib.auth import authenticate

        user = authenticate(email=email, password=password)

        if user:
            if not user.is_active:
                # Handle inactive user case
                raise serializers.ValidationError('User account is inactive.')
        else:
            # Handle invalid credentials case
            raise serializers.ValidationError('Invalid email or password.')

        # Set the authenticated user in the serializer's validated data
        attrs['user'] = user

        return attrs
