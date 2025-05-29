from django.db import models
from django.contrib.auth.models import User



User.add_to_class('section', property(lambda self: self.user.section if hasattr(self, 'user') else None))
User.add_to_class('designation', property(lambda self: self.user.designation if hasattr(self, 'user') else None))

class Position(models.Model):
    SECTION_CHOICES = [
        ('executive', 'Executive'),
        ('managerial', 'Managerial'),
        ('editorial', 'Editorial'),
        ('staff', 'Staff'),
        ('guest', 'Guest'),
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
        default='guest',
    )
    designation = models.CharField(
        max_length=30,
        choices=DESIGNATION_CHOICES,
        default='',
    )
    permission_level = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        response = { 'level': 0 }

        section_levels = {
            'guest': 0,
            'staff': 1,
            'editorial': 2,
            'managerial': 3,
            'executive': 3
        }
        response['level'] = section_levels.get(self.section, 0)
        self.permission_level = response['level']

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.email if self.user.email else self.user.username} - {self.section} - {self.designation}'
