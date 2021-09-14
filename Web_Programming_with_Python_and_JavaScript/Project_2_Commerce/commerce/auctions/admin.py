from auctions.models import Bids, Comments, Listings, User
from auctions.views import register
from django.contrib import admin
from auctions.models import User, Listings, Bids, Comments
# Register your models here.
admin.site.register (User)
admin.site.register (Listings)
admin.site.register (Bids)
admin.site.register (Comments)