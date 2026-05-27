from django.contrib import admin
from .models import Disciplina, FuenteInformacion


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'area', 'grupo', 'nivel_confiabilidad', 'activo')
    list_filter = ('grupo', 'area', 'activo')
    search_fields = ('nombre', 'slug', 'area')
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(FuenteInformacion)
class FuenteInformacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'nivel_confiabilidad', 'activa')
    list_filter = ('tipo', 'activa')
