from django.contrib.auth.models import User, Group
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


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


# создать профиль при создании пользователя
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance
        )
