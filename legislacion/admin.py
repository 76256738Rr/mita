from django.contrib import admin
from .models import IniciativaLegislativa


@admin.register(IniciativaLegislativa)
class IniciativaLegislativaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'estado', 'creado_en')
    list_filter = ('estado',)
