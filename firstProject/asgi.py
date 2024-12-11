import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from api.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firstProject.settings')

# Inicializa la aplicación Django ASGI
django_asgi_app = get_asgi_application()

# Configuración del enrutador ASGI
application = ProtocolTypeRouter({
    # HTTP se maneja a través de Django ASGI (y está configurado con WhiteNoise desde settings.py)
    "http": django_asgi_app,

    # Manejo de WebSockets
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
