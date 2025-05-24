from rest_framework import serializers
from .models import *



class GearSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    used_by = serializers.SerializerMethodField()
    borrowed_by = serializers.SerializerMethodField()

    class Meta:
        model = Gear
        fields = [
            'id',
            'name',
            'used_by',
            'borrowed_by',
            'unit_description',
            'property_number',
            'owner',
            'used',
            'borrowed',
        ]

    def get_owner(self, obj):
        if obj.owner:
            return f'{obj.owner.first_name} {obj.owner.last_name}'.strip() or obj.owner.username
        return None

    def get_used_by(self, obj):
        if hasattr(obj, 'used_by') and obj.used_by:
            return f'{obj.used_by.first_name} {obj.used_by.last_name}'.strip() or obj.used_by.username
        return None

    def get_borrowed_by(self, obj):
        if hasattr(obj, 'borrowed_by') and obj.borrowed_by:
            return f'{obj.borrowed_by.first_name} {obj.borrowed_by.last_name}'.strip() or obj.borrowed_by.username
        return None

class LogSerializer(serializers.ModelSerializer):
    gear = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    slip_id = serializers.SerializerMethodField()
    slipped_by = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()

    class Meta:
        model = Log
        fields = [
            'user',
            'gear',
            'slip_id',
            'slipped_by',
            'action',
            'timestamp',
        ]

    def get_user(self, obj):
        if obj.user:
            return f'{obj.user.first_name} {obj.user.last_name}'.strip() or obj.user.username
        return None

    def get_gear(self, obj):
        if obj.gear.exists():
            return [gear.name for gear in obj.gear.all()]
        return []

    def get_slip_id(self, obj):
        if obj.slip:
            return f'{obj.slip.custom_id}'.strip()

    def get_slipped_by(self, obj):
        if obj.slip:
            return f'{obj.slip.slipped_by.first_name} {obj.slip.slipped_by.last_name}'.strip()

    def get_action(self, obj):
        return obj.get_action_display()

class SlipSerializer(serializers.ModelSerializer):
    gear_borrowed = serializers.SerializerMethodField()
    slipped_by = serializers.SerializerMethodField()

    class Meta:
        model = Slip
        fields = [
            'custom_id',
            'gear_borrowed',
            'slipped_by',
            'condition_before',
            'condition_after',
            'borrowed_date',
            'return_date',
            'expected_return_date',

            'currently_active',
            'for_return',
            'returned',
            'declined',

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
        if obj.slipped_by and obj.slipped_by.first_name and obj.slipped_by.last_name:
            return f'{obj.slipped_by.first_name} {obj.slipped_by.last_name}'.strip()
        elif obj.slipped_by.username:
            return f'{obj.slipped_by.username}'
        return None
