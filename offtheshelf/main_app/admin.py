from django.contrib import admin
from .models import Wishlist, Comment, LetsTry


# Register your models here.
admin.site.register(Wishlist)
admin.site.register(Comment)
admin.site.register(LetsTry)