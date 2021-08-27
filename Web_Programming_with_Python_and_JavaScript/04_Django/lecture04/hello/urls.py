from django.urls import path
from . import views # . is the current directory

urlpatterns = [
    path("", views.index, name="index"),
    path("delyan", views.delyan, name="delyan"),
    path("david", views.david, name="david"),
    path("<str:name>", views.greet, name="greet")
]