from django.urls import path

from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_listing", views.add_listing, name="add_listing"),
    path("<int:listing_id>", views.view_listing, name="view_listing"),
    path("<int:listing_id>/edit", views.edit_listing, name="edit_listing"),
    path("<int:listing_id>/watchlist", views.add_to_watchlist, name="add_to_watchlist"),
    path("<int:listing_id>/WLremoved", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("<int:listing_id>/close", views.close, name="close")
    #path("<int:listing_id>/edit", views.comments, name="comments")

    
]#+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
   # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



