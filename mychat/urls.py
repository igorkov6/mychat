# mysite/urls.py
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', include('chat.urls')),
    path('admin/', admin.site.urls),
    path('social/', include('social_django.urls', namespace='social')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('favicon.ico', RedirectView.as_view(url='static/assets/favicon.ico')),
]
