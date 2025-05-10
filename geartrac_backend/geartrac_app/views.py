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
from geartrac_auth.models import Position



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
                return Response({'message': f'Gear with ID {id} is already borrowed'}, status=status.HTTP_400_BAD_REQUEST)
            if gear.used_by:
                return Response({'message': f'Gear with ID {id} is currently in use'}, status=status.HTTP_400_BAD_REQUEST)

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

            log = Log.objects.create(user=request.user, action=action)
            log.gear.set(gear)
            log.save()

            return Response({'message': 'Gear successfully marked as used'}, status=status.HTTP_200_OK)

        return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        action = request.data.get('action')

        if not action:
            return Response({'error': 'Action is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'unuse':
            gear_id = request.data.get('gear_id')

            if not gear_id:
                return Response({'error': 'Provide a gear_id'}, status=status.HTTP_400_BAD_REQUEST)

            gear = Gear.objects.get(id=gear_id)
            gear.used_by = None
            gear.save()

            return Response({'message': 'Gear successfully marked as unused.'}, status=status.HTTP_200_OK)

        slip_id = request.data.get('slip_id')

        if not slip_id:
            return Response({'error': 'Slip ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

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
        if not request.user.log_access():
            return Response({'error': 'You do not have permission to view logs'}, status=status.HTTP_403_FORBIDDEN)

        logs = Log.objects.all()
        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SlipsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        position = Position.objects.get(user=request.user)
        section = position.section
        designation = position.designation

        if section == 'staff':
            slips = Slip.objects.filter(slipped_by=request.user, currently_active=True, for_return=False)
            serializer = SlipSerializer(slips, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        elif section == 'editorial':
            staff_users = []

            if designation == 'senior_videojournalist':
                staff_positions = Position.objects.filter(
                    designation__in=['videojournalist', 'senior_videojournalist']
                )
                staff_users = [pos.user for pos in staff_positions]
            elif designation == 'senior_photojournalist':
                staff_positions = Position.objects.filter(
                    designation__in=['photojournalist', 'senior_photojournalist']
                )
                staff_users = [pos.user for pos in staff_positions]
            elif designation == 'graphics_design_director':
                staff_positions = Position.objects.filter(
                    designation__in=['layout_artist', 'graphics_design_director']
                )
            elif designation == 'senior_illustrator':
                staff_positions = Position.objects.filter(
                    designation__in=['illustrator', 'senior_illustrator']
                )

            slips = Slip.objects.filter(slipped_by__in=staff_users, currently_active=True, section_editor_signature=False)
            serializer = SlipSerializer(slips, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        elif section in ['managerial', 'executive']:
            slips = []

            if section == 'managerial' and designation == 'circulations_manager':
                archived = request.data.get('archived')

                if archived:
                    slips = Slip.objects.filter(
                        currently_active=False,
                        for_return=False
                    )
                else:
                    slips = Slip.objects.filter(
                        currently_active=True,
                        section_editor_signature=True,
                        circulations_manager_signature=False,
                    ) | Slip.objects.filter(currently_active=False, for_return=True)
            elif section == 'managerial' and designation == 'managing_editor':
                slips = Slip.objects.filter(
                    currently_active=True,
                    section_editor_signature=True,
                    circulations_manager_signature=True,
                    managing_editor_signature=False,
                )
            elif section == 'executive' and designation == 'editor_in_chief':
                slips = Slip.objects.filter(
                    currently_active=True,
                    section_editor_signature=True,
                    circulations_manager_signature=True,
                    managing_editor_signature=True,
                    editor_in_chief_signature=False,
                )

            serializer = SlipSerializer(slips, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def put(self, request):
        position = Position.objects.get(user=request.user)
        section = position.section
        designation = position.designation

        action = request.data.get('action')
        slip_id = request.data.get('slip_id')
        slip = Slip.objects.get(id=slip_id)

        if action == 'acknowledge_return':
            condition_after = request.data.get('condition_after')

            if not condition_after:
                return Response({'error': 'Condition after is required'}, status=status.HTTP_400_BAD_REQUEST)

            slip.for_return = False
            slip.returned = True
            slip.return_date = timezone.now()
            slip.condition_after = condition_after
            slip.save()

            log = Log.objects.create(user=request.user, action=action)
            log.gear.set(slip.gear_borrowed)
            log.save()

            return Response({'message': 'Gear successfully returned'}, status=status.HTTP_200_OK)
        elif action == 'return':
            slip.currently_active = False
            slip.for_return = True

            slip.save()

            return Response({'message': 'Slip is marked for return.'}, status=status.HTTP_200_OK)
        elif action == 'decline':
            if position.permission_level < 2:
                return Response({'error': 'You do not have permission to decline this slip.'}, status=status.HTTP_403_FORBIDDEN)

            slip.currently_active = False
            slip.declined = True

            slip.save()

            return Response({'message': 'Slip was successfully declined.'}, status=status.HTTP_200_OK)
        elif action == 'accept':
            if section == 'editorial':
                slip.section_editor_signature = True
            elif section == 'managerial' and designation == 'circulations_manager':
                slip.circulations_manager_signature = True
            elif section == 'managerial' and designation == 'managing_editor':
                slip.managing_editor_signature = True
            elif section == 'executive' and designation == 'editor_in_chief':
                slip.editor_in_chief_signature = True
            else:
                return Response({'error': 'You have unauthorized section and designation.'}, status=status.HTTP_403_FORBIDDEN)

            slip.save()

            return Response({'message': 'Slip was accepted.'}, status=status.HTTP_200_OK)
