# django package import
from django.contrib import admin
# local import
from favorite_app.models import Category, FavoriteThings

admin.site.register(Category)
admin.site.register(FavoriteThings)
