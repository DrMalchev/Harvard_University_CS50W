from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import datetime


class User(AbstractUser):
    pass

class MyPosts(models.Model):
    postUser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    postBody = models.CharField( max_length=256, default=None)
    timestamp = models.DateTimeField()
    postLikes = models.IntegerField(default=0)

    def __str__(self):
        return f"User: {self.postUser}/ Item: {self.postBody}/ Cat: {self.timestamp}/ Price: {self.postLikes}"