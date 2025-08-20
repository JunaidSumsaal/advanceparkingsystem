import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from core.middleware import JWTAuthMiddleware
import parking.routing
import notifications.routing
import core.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(
                parking.routing.websocket_urlpatterns,
                notifications.routing.websocket_urlpatterns,
                core.routing.websocket_urlpatterns
            )
        )
    ),
})
