# chat/urls.py
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from .viewsets import UsersViewSet, GroupsViewSet

# маршрутизатор REST framework
router = routers.DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'groups', GroupsViewSet)

urlpatterns = [
                  path('', views.dashboard, name='dashboard'),
                  path('api/', include(router.urls)),
                  path('chat/', views.chat, name='chat'),
                  path('dashboard/', views.dashboard, name='dashboard'),
                  path('login/', auth_views.LoginView.as_view(), name='login'),
                  path('logout/', auth_views.LogoutView.as_view(), name='logout'),
                  path('edit/', views.edit, name='edit'),
                  path('register/', views.register, name='register'),
                  path('group/', views.group, name='group'),
                  path('room/<str:room_name>/', views.room, name="room"),
                  path('update/', views.update),
                  path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
                  path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(),
                       name='password_change_done'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
