# main Urls.py 
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blogg.urls')),  # подключаем маршруты из приложения blogg
    path('account/', include('account.urls')),
]
