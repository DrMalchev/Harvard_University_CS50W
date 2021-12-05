from django.urls import path
from . import views
from django.conf import settings 
from django.conf.urls.static import static 


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("placeorder", views.placeorder, name="placeorder"),
    path("myorders", views.myorders, name="myorders"),
    path("waitlist", views.waitlist, name="waitlist"),
    path("edit/<int:id>", views.edit, name="edit"),
    path("delete/<int:id>", views.delete, name="delete"),
    path("taskmanager", views.taskmanager, name="taskmanager"),
    path("metrics", views.metrics, name="metrics"),
    path("blogadmin", views.blogadmin, name="blogadmin"),
    path("deleteuser/<int:id>", views.deleteuser, name="deleteuser"),
    path("blog", views.blog, name="blog"),
    path("fileupload", views.fileupload, name="fileupload"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

