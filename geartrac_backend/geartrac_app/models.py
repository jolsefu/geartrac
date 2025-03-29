from django.db import models
from django.contrib.auth.models import User

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

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user')
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, default='staff_member')
    designation = models.CharField(max_length=30, choices=DESIGNATION_CHOICES, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} - {self.section} - {self.designation}'

class Gear(models.Model):
    name = models.CharField(max_length=40)
    unit_description = models.TextField()
    property_number = models.CharField(max_length=50, unique=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, default=None)

    def __str__(self):
        return f'{self.name} - {self.unit_description} - {self.property_number} - {self.owner}'
