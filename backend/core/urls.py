from django.contrib import admin
from django.urls import include, path
from .views import metrics_view
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('portal/admin/', admin.site.urls),
    path('', include('django_prometheus.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/parking/', include('parking.urls')),
    path('api/notifications/', include('notifications.urls')),
    path("api/metrics/", metrics_view, name="metrics"),
    path('api/dashboard/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
