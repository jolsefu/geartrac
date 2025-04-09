from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
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

from .serializers import *
from .models import *


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
        return Response(status=status.HTTP_200_OK)

class DetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

class GearsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        gears = Gear.objects.all()
        serializer = GearSerializer(gears, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        action = request.data.get('action')
        gear_id = request.data.get('gear_id')

        if not action or not gear_id:
            return Response({'error': 'Action and gear_id are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            gear = Gear.objects.get(id=gear_id)
        except Gear.DoesNotExist:
            return Response({'error': 'Gear not found'}, status=status.HTTP_404_NOT_FOUND)

        if action == 'borrow':
            pass

        elif action == 'use':
            gear.used_by = request.user
            gear.save()

            Log.objects.create(user=request.user, gear=gear, action=action)

            return Response({'message': 'Gear successfully marked as used'}, status=status.HTTP_200_OK)

        elif action == 'return':
            gear.used_by = None
            gear.borrowed_by = None
            gear.save()

            Log.objects.create(user=request.user, gear=gear, action=action)

            return Response({'message': 'Gear successfully marked as returned'}, status=status.HTTP_200_OK)

        return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)
