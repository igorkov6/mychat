from django.contrib.auth.models import User, Group
from django.db import models
from django.conf import settings


class Message(models.Model):
    group = models.ForeignKey(Group, related_name='message', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='message', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='users/', blank=True)

    def __str__(self):
        return 'Profile for user'
