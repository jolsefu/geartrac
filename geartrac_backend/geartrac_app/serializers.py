from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class GearSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(allow_null=True, default=None)

    class Meta:
        model = Gear
        fields = ['name', 'unit_description', 'property_number', 'owner', 'used', 'borrowed']
