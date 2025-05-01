from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Position



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'section',
            'designation',
        ]
