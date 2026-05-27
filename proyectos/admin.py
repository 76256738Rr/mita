from django.contrib import admin
from .models import EjeAccion, LeccionAprendida, ProyectoReferencia


class EjeAccionInline(admin.TabularInline):
    model = EjeAccion
    extra = 0


@admin.register(ProyectoReferencia)
class ProyectoReferenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    inlines = [EjeAccionInline]


@admin.register(LeccionAprendida)
class LeccionAprendidaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'sector', 'institucion', 'anio')
    list_filter = ('sector', 'institucion')
