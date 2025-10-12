#main urls
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include('zz.urls')),
    path("users/", include('users.urls')),
    path('', include('django_prometheus.urls')),
    #path("profiles/", include("users.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
