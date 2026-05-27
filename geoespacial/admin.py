from django.contrib import admin
from .models import CapaGeografica, PuntoAtencionEdomex, ZonaGeografica


@admin.register(ZonaGeografica)
class ZonaGeograficaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'corredor', 'prevalencia', 'mortalidad')
    list_filter = ('tipo', 'corredor', 'pobreza')
    search_fields = ('nombre',)


@admin.register(CapaGeografica)
class CapaGeograficaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(PuntoAtencionEdomex)
class PuntoAtencionEdomexAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'eje', 'tipo', 'municipio', 'telefono')
    list_filter = ('eje', 'municipio', 'tipo')
    search_fields = ('nombre', 'municipio', 'direccion')
    prepopulated_fields = {'slug': ('nombre',)}
