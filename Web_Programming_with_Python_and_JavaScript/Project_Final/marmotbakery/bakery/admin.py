from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Orders, Image, Blog, Content
#from .models import User, UserAdmin

# Register your models here.
admin.site.register(User)
admin.site.register(Orders)
admin.site.register(Image)
admin.site.register(Blog)
admin.site.register(Content)

admin.site.site_header = "MARMOT Bake   *** Admin Site ***"