from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from dj_rest_auth.registration.views import SocialLoginView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from django.views.decorators.csrf import ensure_csrf_cookie

from django.contrib.auth.models import User
from .serializers import UserSerializer

import jwt

from .models import Position


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

@receiver(post_save, sender=User)
def check_email_domain(sender, instance, created, **kwargs):
    if created:
        if not instance.email.endswith("@carsu.edu.ph"):
            instance.delete()
            raise ValidationError({'error': "Only @carsu.edu.ph emails are allowed."})
        else:
            Position.objects.create(user=instance, section="Guest")

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

# https://www.reddit.com/r/django/comments/11eswma/djrestauth_google_login_help_needed_getting/
# ????? weird bug

class CustomGoogleOAuth2Adapter(GoogleOAuth2Adapter):
    def complete_login(self, request, app, token, response, **kwargs):
        try:
            identity_data = jwt.decode(
                response["id_token"],
                options={
                    "verify_signature": False,
                    "verify_iss": True,
                    "verify_aud": True,
                    "verify_exp": True,
                },
                issuer=self.id_token_issuer,
                audience=app.client_id,
            )
        except jwt.PyJWTError as e:
            raise OAuth2Error("Invalid id_token") from e
        login = self.get_provider().sociallogin_from_response(request, identity_data)
        return login

class GoogleLogin(SocialLoginView):
    adapter_class = CustomGoogleOAuth2Adapter
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
            )

        return response

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
            return Response({"error": "Token not found"}, status=status.HTTP_400_BAD_REQUEST)

class ValidateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if Position.objects.get(user=request.user).permission_level == 0:
            return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(status=status.HTTP_200_OK)

class GuestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            position = Position.objects.get(user=request.user)
            if position.permission_level == 0:
                return Response(status=status.HTTP_200_OK)
        except Position.DoesNotExist:
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_403_FORBIDDEN)

class DetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

class PermissionLevelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_position = Position.objects.get(user=request.user)
        response = { 'level': user_position.permission_level }

        return Response(response, status=status.HTTP_200_OK)
