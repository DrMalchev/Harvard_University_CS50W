from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import datetime


class User(AbstractUser):
    followers = models.IntegerField(default=0)
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)

    #pass

class MyPosts(models.Model):
    postUser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    postBody = models.CharField( max_length=256, default=None)
    timestamp = models.DateTimeField()
    postLikes = models.IntegerField(default=0)

    def __str__(self):
        return f"Posted by: {self.postUser}/ Post: {self.postBody}/ Timestamp: {self.timestamp}/ Post Likes: {self.postLikes}"