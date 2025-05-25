"""
ASGI config for geartrac_site project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from .routing import application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geartrac_site.settings')

django_asgi_application = get_asgi_application()

application = application
