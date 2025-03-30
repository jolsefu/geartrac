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
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name='owner'
    )
    used_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_by'
    )

    name = models.CharField(max_length=40)
    unit_description = models.TextField()
    property_number = models.CharField(max_length=50, unique=True)
    used = models.BooleanField(default=False)
    borrowed = models.BooleanField(default=False)

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
        default='good'
    )
    condition_after = models.CharField(
        max_length=10,
        choices=CONDITION_CHOICES,
        default='good',
    )
    borrowed_date = models.DateTimeField(
        null=True,
        blank=True,
        default=timezone.now,
    )
    return_date = models.DateTimeField(
        null=True,
        blank=True
    )
    gear_borrowed = models.ManyToManyField(Gear)

    section_editor_signature = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='section_editor_signature',
    )
    circulations_manager_signature = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='circulations_manager_editor',
    )
    managing_editor_signature = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managing_editor_signature',
    )
    editor_in_chief_signature = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='editor_in_chief_signature',
    )

    def __str__(self):
        return f'{[gear.name for gear in self.gear_borrowed.all()]} - {self.condition_before} - {self.condition_after} - {self.borrowed_date} - {self.return_date}'
