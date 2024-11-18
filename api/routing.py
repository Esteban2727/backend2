# api/routing.py

from django.urls import path
from api.consumers import TriquiConsumer


websocket_urlpatterns = [
    path("ws/triqui/", TriquiConsumer.as_asgi()),  
]
