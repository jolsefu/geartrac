from rest_framework import serializers
from .models import *



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

class SlipSerializer(serializers.ModelSerializer):
    gear_borrowed = serializers.SerializerMethodField()
    slipped_by = serializers.SerializerMethodField()

    class Meta:
        model = Slip
        fields = [
            'gear_borrowed',
            'slipped_by',
            'condition_before',
            'condition_after',
            'borrowed_date',
            'return_date',
            'expected_return_date',
            'section_editor_signature',
            'circulations_manager_signature',
            'managing_editor_signature',
            'editor_in_chief_signature',
        ]

    def get_gear_borrowed(self, obj):
        if obj.gear_borrowed.exists():
            return [gear.name for gear in obj.gear_borrowed.all()]
        return []

    def get_slipped_by(self, obj):
        if obj.slipped_by:
            return f'{obj.slipped_by.first_name} {obj.slipped_by.last_name}'.strip() or obj.user.username
        return None
