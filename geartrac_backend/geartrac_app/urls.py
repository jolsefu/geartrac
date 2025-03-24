from django.urls import include, path, re_path

from .views import GoogleLogin

urlpatterns = [
    path('v1/auth/', include('dj_rest_auth.urls')),
    re_path(r'^v1/auth/accounts/', include('allauth.urls')),
    path('v1/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('v1/auth/google/', GoogleLogin.as_view(), name='google_login'),
    # path(
    #     'api/v1/auth/google/callback/',
    #     GoogleLoginCallback.as_view(),
    #     name='google_login_callback',
    # ),
]
