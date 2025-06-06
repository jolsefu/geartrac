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

    custom_id = models.CharField(max_length=10)
    slipped_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='slipped_by',
        null=True,
        blank=True,
    )

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

    currently_active = models.BooleanField(default=True)
    for_return = models.BooleanField(default=False)
    returned = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)

    section_editor_signature = models.BooleanField(default=False)
    circulations_manager_signature = models.BooleanField(default=False)
    managing_editor_signature = models.BooleanField(default=False)
    editor_in_chief_signature = models.BooleanField(default=False)

    gear_borrowed = models.ManyToManyField(
        Gear,
        related_name='gear_borrowed',
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.custom_id:
            year = timezone.now().year
            self.custom_id = f'{year}-{str(self.id).zfill(3)}'

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

    def delete(self, *args, **kwargs):
        for gear in self.gear_borrowed.all():
            gear.borrowed_by = None
            gear.borrowed = False
            gear.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f'{self.custom_id} - {self.slipped_by.email}'

class Log(models.Model):
    actions = [
        ('use', 'Use'),
        ('unuse', 'Unuse'),
        ('borrow', 'Borrow'),
        ('slip_confirmed', 'Slip Confirmed'),
        ('for_return', 'For Return'),
        ('confirm_return', 'Confirm Return'),
        ('declined', 'Declined'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='log_user',
    )
    gear = models.ManyToManyField(
        Gear,
        related_name='log_gear',
    )
    slip = models.ForeignKey(
        Slip,
        on_delete=models.CASCADE,
        related_name='log_slip',
        null=True,
        blank=True,
    )

    action = models.CharField(max_length=50, choices=actions)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.email} - {self.action} - {self.timestamp}'

class CustomNotification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipient")
    message = models.CharField(max_length=100)
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
