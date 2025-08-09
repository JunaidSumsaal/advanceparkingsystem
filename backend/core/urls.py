from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('portal/admin/', admin.site.urls),
    path('', include('django_prometheus.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/parking/', include('parking.urls')),
    path('api/notifications/', include('notifications.urls')),
]
