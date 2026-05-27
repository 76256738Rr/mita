from django.contrib import admin
from .models import SaberTradicional


@admin.register(SaberTradicional)
class SaberTradicionalAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'comunidad', 'validado')
    list_filter = ('comunidad', 'validado')
    search_fields = ('titulo', 'descripcion')
