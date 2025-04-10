from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Position(models.Model):
    SECTION_CHOICES = [
        ('executive', 'Executive'),
        ('managerial', 'Managerial'),
        ('editorial', 'Editorial'),
        ('staff', 'Staff'),
    ]

    DESIGNATION_CHOICES = [
        ('layout_artist', 'Layout Artist'),
        ('graphics_design_director', 'Graphics Design Director'),

        ('videojournalist', 'Videojournalist'),
        ('senior_videojournalist', 'Senior Videojournalist'),

        ('photojournalist', 'Photojournalist'),
        ('senior_photojournalist', 'Senior Photojournalist'),

        ('illustrator', 'Illustrator'),
        ('senior_illustrator', 'Senior Illustrator'),

        ('opinion_writer', 'Opinion Writer'),
        ('opinion_editor', 'Opinion Editor'),

        ('literary_writer', 'Literary Writer'),
        ('literary_editor', 'Literary Editor'),

        ('sports_writer', 'Sports Writer'),
        ('sports_editor', 'Sports Editor'),

        ('news_writer', 'News Writer'),
        ('news_editor', 'News Editor'),

        ('feature_writer', 'Feature Writer'),
        ('feature_editor', 'Feature Editor'),

        ('newsletter_editor', 'Newsletter Editor'),

        ('human_resources_manager', 'Human Resources Manager'),
        ('online_accounts_manager', 'Online Accounts Manager'),
        ('circulations_manager', 'Circulations Manager'),
        ('associate_managing_editor', 'Associate Managing Editor'),

        ('managing_editor', 'Managing Editor'),
        ('technical_editor', 'Technical Editor'),
        ('creative_director', 'Creative Director'),
        ('editor_in_chief', 'Editor-in-Chief'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='user',
    )
    section = models.CharField(
        max_length=20,
        choices=SECTION_CHOICES,
        default='staff_member',
    )
    designation = models.CharField(
        max_length=30,
        choices=DESIGNATION_CHOICES,
        default='',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} - {self.section} - {self.designation}'

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
    unit_description = models.TextField()
    property_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    used = models.BooleanField(default=False)
    borrowed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.used = self.used_by is not None
        self.borrowed = self.borrowed_by is not None
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} - {self.property_number} - {self.owner} - {self.unit_description}'

class Slip(models.Model):
    CONDITION_CHOICES = [
        ('great', 'Great'),
        ('good', 'Good'),
        ('bad', 'Bad'),
        ('broken', 'Broken'),
    ]

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

    def __str__(self):
        return f'{[gear.name for gear in self.gear_borrowed.all()]} - {self.condition_before} - {self.condition_after} - {self.borrowed_date} - {self.return_date}'

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
