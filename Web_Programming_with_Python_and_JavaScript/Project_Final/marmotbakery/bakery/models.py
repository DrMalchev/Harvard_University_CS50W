
import datetime
from typing_extensions import Concatenate
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from bakery.forms import UserCreationForm


class User(AbstractUser):
    cancelations = models.IntegerField(default=0, null=False)
    def __str__(self):
        return f"{self.username}  {self.first_name} {self.last_name}"
    pass

class Orders(models.Model):
    breadType = (
        ('White Bread', 'White Bread'),
        ('Country Bread', 'Country Bread'),
        ('Oat Porridge Bread', 'Oat Porridge Bread'),
        ('Semolina Bread', 'Semolina Bread'),
        ('100% Rye Bread', '100% Rye Bread'),
        ('Seeded', 'Seeded'),
        ('Baguette', 'Baguette'),
        ('Sweet Brioche', 'Sweet Brioche')
    )

    firstName = models.CharField(max_length=64)
    lastName = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    postCode = models.IntegerField()
    addressL1 = models.CharField(max_length=64)
    addressL2 = models.CharField(max_length=64)
    comment = models.CharField(max_length=256)
    breadType = models.CharField(max_length=64, choices=breadType)
    quantity = models.IntegerField(default=0, null=False)
    tel = models.IntegerField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    price = models.CharField(default=0, max_length=64)
    orderTime = models.DateTimeField(default=datetime.datetime.now)
    cumulative = models.IntegerField(default=0)
    cumulativeMax = models.IntegerField(default=0)
    brake = models.BooleanField(default=False)
    deliveryTime = models.DateTimeField(default=datetime.datetime.now)
    processed = models.IntegerField(default=0, null=False)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.owner} >> {self.breadType} | {self.quantity}x | Delivery: {self.deliveryTime.date()}"
###
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'is_bot_flag', 'password1', 'password2')}
        ),
    )
class Content(models.Model):
    content = models.TextField(null=True)
    blogid = models.IntegerField(default=0, null=False)
    number = models.IntegerField(default=0, null=False)
    isTitleImage = models.BooleanField(default=False)

class Image(models.Model):
    file = models.FileField(upload_to='', null=True, blank=True)
    filepath = models.CharField(null=True,max_length=999)
    filename = models.CharField(null=True, max_length=256)
    blogid = models.IntegerField(default=0, null=False)
    number = models.IntegerField(default=0, null=False)

class Blog(models.Model):
    blogid = models.IntegerField(default=0, null=False)