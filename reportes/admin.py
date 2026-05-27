from django.contrib import admin
from .models import IndicadorImpacto


@admin.register(IndicadorImpacto)
class IndicadorImpactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'sector', 'valor_actual', 'meta', 'unidad')
    list_filter = ('sector', 'tendencia')
