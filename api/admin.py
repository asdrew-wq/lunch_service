from django.contrib import admin
from .models import Restaurant, Menu, Vote

# Register your models here.
admin.site.register(Restaurant)
admin.site.register(Menu)
admin.site.register(Vote)
