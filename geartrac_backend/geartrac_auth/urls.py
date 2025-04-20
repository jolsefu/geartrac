from django.urls import path
from .views import *



urlpatterns = [
    path('csrf/', get_csrf_token, name='csrf_token'),
    path('google/', GoogleLogin.as_view(), name='google_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('validate/', ValidateView.as_view(), name='validate'),
    path('details/', DetailsView.as_view(), name='details'),
]
