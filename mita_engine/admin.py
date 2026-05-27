from django.contrib import admin
from .models import (
    CruceInterdisciplinario, Dictamen, EjeMITA, Expediente,
    OpcionSolucion, PasoProceso, PropuestaEvaluacion,
    TareaExpediente, TransicionExpediente,
)


class TransicionInline(admin.TabularInline):
    model = TransicionExpediente
    extra = 0
    readonly_fields = ('creado_en',)


class TareaInline(admin.TabularInline):
    model = TareaExpediente
    extra = 0


class OpcionInline(admin.TabularInline):
    model = OpcionSolucion
    extra = 0


@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    list_display = ('folio', 'titulo', 'paso_actual', 'estado', 'responsable', 'actualizado_en')
    list_filter = ('estado', 'paso_actual')
    search_fields = ('folio', 'titulo', 'solicitante')
    inlines = [TransicionInline, TareaInline, OpcionInline]


@admin.register(TareaExpediente)
class TareaExpedienteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'expediente', 'paso', 'completada', 'rol_requerido', 'vencimiento')
    list_filter = ('completada', 'tipo', 'rol_requerido')


@admin.register(TransicionExpediente)
class TransicionExpedienteAdmin(admin.ModelAdmin):
    list_display = ('expediente', 'paso_anterior', 'paso_nuevo', 'accion', 'usuario', 'creado_en')
    list_filter = ('accion',)


@admin.register(EjeMITA)
class EjeMITAAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'sigla')
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(PasoProceso)
class PasoProcesoAdmin(admin.ModelAdmin):
    list_display = ('paso', 'nombre')


@admin.register(CruceInterdisciplinario)
class CruceInterdisciplinarioAdmin(admin.ModelAdmin):
    list_display = ('concepto',)


@admin.register(PropuestaEvaluacion)
class PropuestaEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'estado', 'puntuacion_total', 'aprobado', 'creado_en')
    list_filter = ('estado', 'aprobado')
    search_fields = ('titulo', 'solicitante')


@admin.register(Dictamen)
class DictamenAdmin(admin.ModelAdmin):
    list_display = ('folio', 'resultado', 'puntuacion', 'emitido_en')
    list_filter = ('resultado', 'nivel_fronesis')
    search_fields = ('folio',)


@admin.register(OpcionSolucion)
class OpcionSolucionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'expediente', 'puntuacion', 'seleccionada')
