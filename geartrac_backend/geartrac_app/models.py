from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    ACCESS_LEVELS = [
        (1, 'Executives or Manager'),
        (2, 'Section Editor'),
        (3, 'Staff Member'),
    ]

    groups = models.ManyToManyField(Group, related_name="custom_user_set")
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions")

    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    access_level = models.IntegerField(choices=ACCESS_LEVELS, default=3)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
