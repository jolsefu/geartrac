from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from geartrac_auth.models import Position



def log_access(self):
    try:
        position = self.user
        return position.section in ['editorial', 'managerial', 'executive']
    except Position.DoesNotExist:
        return False

User.add_to_class('log_access', log_access)

class Gear(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name='owner',
    )
    used_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_by',
    )
    borrowed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='borrowed_by',
    )

    name = models.CharField(max_length=40)
    unit_description = models.TextField(blank=True)
    property_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    used = models.BooleanField(default=False)
    borrowed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.used = self.used_by is not None
        self.borrowed = self.borrowed_by is not None
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.property_number} - {self.name} - {self.owner}'

class Slip(models.Model):
    CONDITION_CHOICES = [
        ('great', 'Great'),
        ('good', 'Good'),
        ('bad', 'Bad'),
        ('broken', 'Broken'),
    ]

    slipped_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='slipped_by',
        null=True,
        blank=True,
    )
    currently_active = models.BooleanField(default=True)

    condition_before = models.CharField(
        max_length=10,
        choices=CONDITION_CHOICES,
        default='good',
    )
    condition_after = models.CharField(
        max_length=10,
        choices=CONDITION_CHOICES,
        default='good',
    )

    borrowed_date = models.DateTimeField(
        null=True,
        blank=True,
    )
    return_date = models.DateTimeField(
        null=True,
        blank=True,
    )
    expected_return_date = models.DateTimeField(
        null=True,
        blank=True,
    )

    section_editor_signature = models.BooleanField(default=False)
    circulations_manager_signature = models.BooleanField(default=False)
    managing_editor_signature = models.BooleanField(default=False)
    editor_in_chief_signature = models.BooleanField(default=False)

    gear_borrowed = models.ManyToManyField(
        Gear,
        related_name='gear_borrowed',
    )

    slip_id = models.CharField(max_length=8, unique=True)

    def save(self, *args, **kwargs):
        if not self.slip_id:
            year = timezone.now().year
            super().save(*args, **kwargs)
            self.slip_id = f'{year}-{str(self.id).zfill(3)}'

        super().save(*args, **kwargs)

        if self.currently_active:
            for gear in self.gear_borrowed.all():
                gear.borrowed_by = self.slipped_by
                gear.borrowed = True
                gear.save()
        else:
            for gear in self.gear_borrowed.all():
                gear.borrowed_by = None
                gear.borrowed = False
                gear.save()

    def __str__(self):
        return f'{self.slipped_by}'

class Log(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='log_user',
    )
    gear = models.ManyToManyField(
        Gear,
        related_name='log_gear',
    )

    action = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} - {self.action} - {self.timestamp}'

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.recipient}: {self.message[:20]}"
