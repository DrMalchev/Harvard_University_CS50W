from django.urls import path
from . import views

app_name = "tasks"
urlpatterns = [
    path("", views.index, name="index"),
    path("add", views.add, name="add") 
    #when I go to /tasks/add -> call function add -> call it add
]