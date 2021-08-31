from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title_name>/", views.title, name="title"),
    path("search", views.search, name="search"),
    path("new", views.new, name="new"),
    path("wiki/<str:title>/edit", views.edit, name="edit"),
    path("wiki/<str:title>/delete", views.delete, name="delete"),
    path("random_page", views.random_page, name="random_page")
    ]
