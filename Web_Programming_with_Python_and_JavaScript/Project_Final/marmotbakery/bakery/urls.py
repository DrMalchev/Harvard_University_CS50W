from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("placeorder", views.placeorder, name="placeorder"),
    path("myorders", views.myorders, name="myorders"),
    path("waitlist", views.waitlist, name="waitlist")
]
