from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from django.contrib.postgres.search import TrigramSimilarity

from .serializers import *
from .models import *
from geartrac_auth.models import Position

from django.utils.dateparse import parse_date

from .utils import create_and_send_notification



class GearsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        request_user_owner = request.query_params.get('request_user_owner')
        if request_user_owner:
            request_user_owner = request_user_owner.lower() == 'true'
        else:
            request_user_owner = False

        search_query = request.query_params.get('search', '')

        if request_user_owner:
            gears = Gear.objects.filter(
                used_by=request.user
            ) | Gear.objects.filter(
                borrowed_by=request.user
            )
        else:
            gears = Gear.objects.all()

        try:
            available = request.query_params.get('available').lower() == 'true'
        except AttributeError:
            available = None

        if available is True:
            gears = gears.filter(used_by=None, borrowed_by=None)
        elif available is False:
            gears = gears.exclude(used_by=None, borrowed_by=None)

        gears = gears.order_by('id')

        if search_query:
            gears = gears.annotate(
                similarity=TrigramSimilarity(
                    'name',
                    search_query
                )).filter(similarity__gt=0.01).order_by('-similarity')

        paginator = PageNumberPagination()
        paginator.page_size = 3

        result_page = paginator.paginate_queryset(gears, request)
        serializer = GearSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

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

        gears = Gear.objects.filter(id__in=gear_id)

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
            slip.gear_borrowed.set(gears)
            slip.save()

            log = Log.objects.create(user=request.user, action=action)
            log.slip = slip
            log.gear.set(gears)
            log.save()

            designation = Position.objects.get(user=request.user).designation
            message = f"{request.user.first_name} {request.user.last_name} has issued a borrower's slip #{slip.custom_id}"
            recipient = None

            if designation == "videojournalist":
                recipient = Position.objects.get(designation="senior_videojournalist").user
            elif designation == "photojournalist":
                recipient = Position.objects.get(designation="senior_photojournalist").user
            elif designation == "illustrator":
                recipient = Position.objects.get(designation="senior_illustrator").user

            CustomNotification.objects.create(recipient=recipient, message=message)

            return Response({'message': 'Gear/s successfully borrowed'}, status=status.HTTP_200_OK)

        elif action == 'use':
            for gear in gears:
                gear.used_by = request.user
                gear.save()

            log = Log.objects.create(user=request.user, action=action)
            log.gear.set(gears)
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

            gears = Gear.objects.filter(id__in=gear_id)
            for gear in gears:
                gear.used_by = None
                gear.save()

            log = Log.objects.create(user=request.user, action=action)
            log.gear.set(gears)
            log.save()

            return Response({'message': 'Gear successfully marked as unused.'}, status=status.HTTP_200_OK)

        return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)

class LogsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.log_access():
            return Response({'error': 'You do not have permission to view logs'}, status=status.HTTP_403_FORBIDDEN)

        search_query = request.query_params.get('search', '')
        action = request.query_params.get('action', '')
        date = request.query_params.get('date', '')

        logs = Log.objects.all()

        if date:
            date = parse_date(date)
            logs = logs.filter(timestamp__date=date)

        if search_query:
            logs = logs.annotate(
                similarity=TrigramSimilarity('user__username', search_query) +
                           TrigramSimilarity('gear__name', search_query)
            ).filter(similarity__gt=0.03).order_by('-similarity')

        if action:
            logs = logs.filter(action=action)

        logs = logs.order_by('-timestamp')

        paginator = PageNumberPagination()
        paginator.page_size = 5

        result_page = paginator.paginate_queryset(logs, request)
        serializer = LogSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

class SlipsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        position = Position.objects.get(user=request.user)
        section = position.section
        designation = position.designation

        slips = Slip.objects.none()

        archived = request.query_params.get('archived', 'false').lower() == 'true'
        active = request.query_params.get('active', 'false').lower() == 'true'
        approvals = request.query_params.get('approvals', 'false').lower() == 'true'

        if section == 'staff':
            if archived:
                slips = Slip.objects.filter(
                    slipped_by=request.user,
                    declined=True
                ) | Slip.objects.filter(slipped_by=request.user, returned=True)
            else:
                slips = Slip.objects.filter(slipped_by=request.user, currently_active=True)
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

            if archived:
                slips = Slip.objects.filter(
                    slipped_by__in=staff_users,
                    declined=True
                ) | Slip.objects.filter(slipped_by__in=staff_users, returned=True)
            else:
                slips = Slip.objects.filter(slipped_by__in=staff_users, currently_active=True, section_editor_signature=False)
        elif section in ['managerial', 'executive']:
            slips = []

            if archived:
                slips = Slip.objects.filter(
                    declined=True
                ) | Slip.objects.filter(returned=True)
            elif active:
                slips = Slip.objects.filter(currently_active=True) | Slip.objects.filter(for_return=True)
            elif approvals:
                if section == 'managerial' and designation == 'circulations_manager':
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
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

        search_query = request.query_params.get('search', '')

        if search_query:
            slips = slips.annotate(
                similarity=TrigramSimilarity(
                    'custom_id',
                    search_query
                )).filter(similarity__gt=0.5).order_by('-similarity')

            print(slips)
        else:
            slips = slips.order_by('-custom_id')


        paginator = PageNumberPagination()
        paginator.page_size = 3

        result_page = paginator.paginate_queryset(slips, request)
        serializer = SlipSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def put(self, request):
        position = Position.objects.get(user=request.user)
        section = position.section
        designation = position.designation

        action = request.data.get('action')
        slip_id = request.data.get('slip_id')

        try:
            slip = Slip.objects.get(custom_id=slip_id)
        except Slip.DoesNotExist:
            return Response({'error': 'Slip not found'}, status=status.HTTP_404_NOT_FOUND)

        if action == 'confirm_return':
            condition_after = request.data.get('condition_after')

            if not condition_after:
                return Response({'error': 'Condition after is required'}, status=status.HTTP_400_BAD_REQUEST)

            slip.for_return = False
            slip.returned = True
            slip.return_date = timezone.now()
            slip.condition_after = condition_after
            slip.save()

            log = Log.objects.create(user=request.user, action=action)
            log.slip = slip
            log.gear.set(slip.gear_borrowed.all())
            log.save()

            message = f"Slip #{slip.custom_id} was successfully returned!"

            CustomNotification.objects.create(recipient=slip.slipped_by, message=message)

            return Response({'message': 'Gear successfully returned'}, status=status.HTTP_200_OK)
        elif action == 'for_return':
            if slip.slipped_by != request.user:
                return Response({'error': 'You are not the owner of this slip.'}, status=status.HTTP_400_BAD_REQUEST)

            slip.currently_active = False
            slip.for_return = True

            log = Log.objects.create(user=request.user, action=action)
            log.slip = slip
            log.gear.set(slip.gear_borrowed.all())
            log.save()

            slip.save()

            message = f"Slip #{slip.custom_id} is waiting for your approval to return!"
            recipient = Position.objects.get(designation='circulations_manager').user

            CustomNotification.objects.create(recipient=recipient, message=message)

            return Response({'message': 'Slip is marked for return.'}, status=status.HTTP_200_OK)
        elif action == 'declined':
            if position.permission_level < 2:
                return Response({'error': 'You do not have permission to decline this slip.'}, status=status.HTTP_403_FORBIDDEN)

            slip.currently_active = False
            slip.declined = True

            slip.save()

            log = Log.objects.create(user=request.user, action=action)
            log.slip = slip
            log.gear.set(slip.gear_borrowed.all())
            log.save()

            message = f"Unfortunately, your slip #{slip.custom_id} has been declined."
            CustomNotification.objects.create(recipient=slip.slipped_by, message=message)

            return Response({'message': 'Slip was successfully declined.'}, status=status.HTTP_200_OK)
        elif action == 'accept':
            if section == 'editorial':
                slip.section_editor_signature = True

                message = f"{slip.slipped_by.first_name} {slip.slipped_by.last_name}'s slip #{slip.custom_id} is waiting for your approval!"
                recipient = Position.objects.get(designation='circulations_manager').user
                CustomNotification.objects.create(recipient=recipient, message=message)

                message = f"Your slip #{slip.custom_id} was approved by your Section Editor!"
                CustomNotification.objects.create(recipient=slip.slipped_by, message=message)
            elif section == 'managerial' and designation == 'circulations_manager':
                slip.circulations_manager_signature = True

                message = f"{slip.slipped_by.first_name} {slip.slipped_by.last_name}'s slip #{slip.custom_id} is waiting for your approval!"
                recipient = Position.objects.get(designation='managing_editor').user
                CustomNotification.objects.create(recipient=recipient, message=message)

                message = f"Your slip #{slip.custom_id} was approved by the Circulations Manager!"
                CustomNotification.objects.create(recipient=slip.slipped_by, message=message)
            elif section == 'managerial' and designation == 'managing_editor':
                slip.managing_editor_signature = True

                message = f"{slip.slipped_by.first_name} {slip.slipped_by.last_name}'s slip #{slip.custom_id} is waiting for your approval!"
                recipient = Position.objects.get(designation='editor_in_chief').user
                CustomNotification.objects.create(recipient=recipient, message=message)

                message = f"Your slip #{slip.custom_id} was approved by the Managing Editor!"
                CustomNotification.objects.create(recipient=slip.slipped_by, message=message)
            elif section == 'executive' and designation == 'editor_in_chief':
                slip.editor_in_chief_signature = True

                log = Log.objects.create(user=request.user, action='slip_confirmed')
                log.slip = slip
                log.gear.set(slip.gear_borrowed.all())
                log.save()

                message = f"Your slip #{slip.custom_id} has been approved by the Editor-in-Chief!"
                CustomNotification.objects.create(recipient=slip.slipped_by, message=message)
            else:
                return Response({'error': 'You have unauthorized section and designation.'}, status=status.HTTP_403_FORBIDDEN)

            slip.save()

            return Response({'message': 'Slip was accepted.'}, status=status.HTTP_200_OK)

class NotifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        action = request.data.get('action')

        if action == 'mark_as_read':
            notification_id = request.data.get('notification_id')

            try:
                notification = CustomNotification.objects.get(id=notification_id)
            except CustomNotification.DoesNotExist:
                return Response({'error': 'Invalid notification id'}, status=status.HTTP_400_BAD_REQUEST)

            notification.read = True
            notification.save()

        if action == 'mark_all_as_read':
            notifications = CustomNotification.objects.filter(recipient=request.user, read=False)
            for notification in notifications:
                notification.read = True
                notification.save()

        if action == "delete_notification":
            notification_id = request.data.get('notification_id')

            try:
                notification = CustomNotification.objects.filter(id=notification_id)
            except CustomNotification.DoesNotExist:
                return Response({'error': 'Invalid notification id'}, status=status.HTTP_400_BAD_REQUEST)

            notification.delete()

        return Response({}, status=status.HTTP_200_OK)
