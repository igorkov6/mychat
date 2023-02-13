# контроллеры REST framework
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from .serializers import UsersSerializer, GroupsSerializer
from loguru import logger


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer


class GroupsViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.exclude(name__startswith='group_')
    serializer_class = GroupsSerializer
