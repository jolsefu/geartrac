from django.urls import path
from .views import *



urlpatterns = [
    path('gear/', GearsView.as_view(), name='gears'),
    path('log/', LogsView.as_view(), name='logs'),
    path('slip/', SlipsView.as_view(), name='slips'),
    path('notification/', NotifyView.as_view(), name='notification'),
]
