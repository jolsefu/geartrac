from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class GearSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    used_by = serializers.SerializerMethodField()

    class Meta:
        model = Gear
        fields = ['name', 'used_by', 'unit_description', 'property_number', 'owner', 'used', 'borrowed']

    def get_owner(self, obj):
        if obj.owner:
            return f'{obj.owner.first_name} {obj.owner.last_name}'.strip() or obj.owner.username
        return None

    def get_used_by(self, obj):
        if hasattr(obj, 'used_by') and obj.used_by:
            return f'{obj.used_by.first_name} {obj.used_by.last_name}'.strip() or obj.used_by.username
        return None

class LogSerializer(serializers.ModelSerializer):
    gear = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Log
        fields = ['gear', 'user', 'action', 'timestamp']

    def get_gear(self, obj):
        if obj.gear.exists():
            return [gear.name for gear in obj.gear.all()]
        return []

    def get_user(self, obj):
        if obj.user:
            return f'{obj.user.first_name} {obj.user.last_name}'.strip() or obj.user.username
        return None
