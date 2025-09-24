import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog_with_ai_bot.settings")

django_asgi_app = get_asgi_application()

import zz.routing  # тут будут вебсокеты

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(zz.routing.websocket_urlpatterns)
    ),
})
