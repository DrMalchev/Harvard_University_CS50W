from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Orders
#from .models import User, UserAdmin

# Register your models here.
admin.site.register(User)
admin.site.register(Orders)

admin.site.site_header = "MARMOT Bake   *** Admin Site ***"