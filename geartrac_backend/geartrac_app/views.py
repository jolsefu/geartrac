from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
# from django.conf import settings

# from urllib.parse import urljoin

# import requests
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

User = get_user_model()

@receiver(post_save, sender=User)
def check_email_domain(sender, instance, created, **kwargs):
    if created and not instance.email.endswith("@carsu.edu.ph"):
        instance.delete()
        raise ValidationError("Only @carsu.edu.ph emails are allowed.")

class CustomGoogleOAuth2Client(OAuth2Client):
    def __init__(
        self,
        request,
        consumer_key,
        consumer_secret,
        access_token_method,
        access_token_url,
        callback_url,
        _scope,  # This is fix for incompatibility between django-allauth==65.3.1 and dj-rest-auth==7.0.1
        scope_delimiter=" ",
        headers=None,
        basic_auth=False,
    ):
        super().__init__(
            request,
            consumer_key,
            consumer_secret,
            access_token_method,
            access_token_url,
            callback_url,
            scope_delimiter,
            headers,
            basic_auth,
        )

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'postmessage'
    client_class = CustomGoogleOAuth2Client

# class GoogleLoginCallback(APIView):
#     def get(self, request, *args, **kwargs):
#         """
#         If you are building a fullstack application (eq. with React app next to Django)
#         you can place this endpoint in your frontend application to receive
#         the JWT tokens there - and store them in the state
#         """

#         code = request.GET.get("code")

#         if code is None:
#             return Response(status=status.HTTP_400_BAD_REQUEST)

#         # Remember to replace the localhost:8000 with the actual domain name before deployment
#         token_endpoint_url = urljoin("http://localhost:8000", reverse("google_login"))
#         response = requests.post(url=token_endpoint_url, data={"code": code})

#         return Response(response.json(), status=status.HTTP_200_OK)
