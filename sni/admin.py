from django.contrib import admin
from .models import InvestigadorSNI, PerfilSNI


@admin.register(PerfilSNI)
class PerfilSNIAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'area', 'nivel', 'activo')
    list_filter = ('area', 'nivel')


@admin.register(InvestigadorSNI)
class InvestigadorSNIAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'area_especialidad', 'nivel_snii', 'disponible')
    list_filter = ('nivel_snii', 'disponible')
    search_fields = ('nombre', 'area_especialidad')
