from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from django.views.decorators.csrf import ensure_csrf_cookie

"""
    CSRF Cookie Authentication
"""

@api_view(['GET'])
@ensure_csrf_cookie
def get_csrf_token(request):
    return Response({ 'message': 'CSRF cookie set' })

"""
    Create only accounts that ends with carsu.edu.ph
"""

User = get_user_model()

@receiver(post_save, sender=User)
def check_email_domain(sender, instance, created, **kwargs):
    if created and not instance.email.endswith("@carsu.edu.ph"):
        instance.delete()
        raise ValidationError("Only @carsu.edu.ph emails are allowed.")

"""
    GoogleOAuth2CLient and GoogleLogin(SocialLoginView)
    handles the google auth code sent by the frontend
    to ensure that they logged in using a verified email
"""

class CustomGoogleOAuth2Client(OAuth2Client):
    def __init__(
        self,
        request,
        consumer_key,
        consumer_secret,
        access_token_method,
        access_token_url,
        callback_url,
        _scope,
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

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200 and response.data['key']:
            token = response.data['key']

            response.set_cookie(
                'access_token',
                token,
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=3600,
            )

        return response

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = Token.objects.get(user=request.user)
        return Response({"message": f"Hello, {request.user.username}, {token}, {request}"})

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            response = Response({ 'message': 'Logged out successfully' })
            response.delete_cookie('access_token')
            token = Token.objects.get(user=request.user)
            token.delete()
            return response
        except Token.DoesNotExist:
            return Response({"error": "Token not found"}, status=400)
