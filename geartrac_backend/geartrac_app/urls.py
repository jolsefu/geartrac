from django.urls import include, path, re_path

from .views import *

urlpatterns = [
    path("auth/csrf/", get_csrf_token, name="csrf_token"),
    path('auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/validate/', ValidateView.as_view(), name='validate'),
    path('auth/details/', DetailsView.as_view(), name='details'),

    path('gear/', GearsView.as_view(), name='gears'),
    path('log/', LogsView.as_view(), name='logs'),
]
