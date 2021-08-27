from django.urls import path
from . import views # . is the current directory

urlpatterns = [
    path("", views.index, name="index")
]