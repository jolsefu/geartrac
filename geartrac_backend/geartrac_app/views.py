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
            return Response({'error': 'Action and Gears are required'}, status=status.HTTP_400_BAD_REQUEST)

        for id in gear_id:
            try:
                gear = Gear.objects.get(id=id)
            except Gear.DoesNotExist:
                return Response({'error': 'Gear not found'}, status=status.HTTP_400_BAD_REQUEST)

            if gear.borrowed_by:
                return Response({'message': f'Gear with ID {id} is already borrowed'}, status=status.HTTP_200_OK)
            if gear.used_by:
                return Response({'message': f'Gear with ID {id} is currently in use'}, status=status.HTTP_200_OK)

        gear = Gear.objects.filter(id__in=gear_id)

        if action == 'borrow':
            if not request.data.get('expected_return_date'):
                return Response({'error': 'Expected return date is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not request.data.get('condition_before'):
                return Response({'error': 'Condition before is required'}, status=status.HTTP_400_BAD_REQUEST)

            slip = Slip.objects.create(
                slipped_by=request.user,
                condition_before=request.data.get('condition_before'),
                borrowed_date=timezone.now(),
                expected_return_date=request.data.get('expected_return_date'),
            )
            slip.gear_borrowed.set(gear)
            slip.save()

            log = Log.objects.create(user=request.user, action=action)
            log.gear.set(gear)
            log.save()

            return Response({'message': 'Gear/s successfully borrowed'}, status=status.HTTP_200_OK)

        elif action == 'use':
            for g in gear:
                g.used_by = request.user
                g.save()

            Log.objects.create(user=request.user, gear=gear, action=action)

            return Response({'message': 'Gear successfully marked as used'}, status=status.HTTP_200_OK)

        return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        slip_id = request.data.get('slip_id')
        action = request.data.get('action')

        if not slip_id or not action:
            return Response({'error': 'Slip ID and action are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            slip = Slip.objects.get(id=slip_id)
        except Slip.DoesNotExist:
            return Response({'error': 'Slip not found'}, status=status.HTTP_404_NOT_FOUND)

        if slip.slipped_by != request.user:
            return Response({'error': 'You cannot modify this slip'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'return':
            condition_after = request.data.get('condition_after')

            if not condition_after:
                return Response({'error': 'Condition after is required'}, status=status.HTTP_400_BAD_REQUEST)

            Slip.return_date = timezone.now()
            Slip.condition_after = condition_after
            Slip.save()

            Log.objects.create(user=request.user, gear=Slip.gear_borrowed, action=action)

            return Response({'message': 'Gear successfully returned'}, status=status.HTTP_200_OK)

        return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)

class LogsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = Log.objects.all()
        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

