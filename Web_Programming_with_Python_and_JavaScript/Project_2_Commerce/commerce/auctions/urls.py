from django.urls import path

from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_listing", views.add_listing, name="add_listing")
    
]#+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
   # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



