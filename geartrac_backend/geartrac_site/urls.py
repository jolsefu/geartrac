from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('geartrac_auth.urls')),
    path('api/', include('geartrac_app.urls')),
]
