from django.contrib import admin

# Register your models here.
from .models import Collection, Text

admin.site.register(Collection)
admin.site.register(Text)