from django.contrib import admin
from .models import MensajeReporteCiudadano, PerfilUsuario, RegistroAuditoria, ReporteCiudadano


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol', 'dependencia')
    list_filter = ('rol',)
    search_fields = ('usuario__username', 'dependencia')


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('accion', 'entidad', 'usuario', 'creado_en')
    list_filter = ('accion', 'entidad')
    readonly_fields = ('creado_en',)


@admin.register(ReporteCiudadano)
class ReporteCiudadanoAdmin(admin.ModelAdmin):
    list_display = ('numero_control', 'eje', 'titulo', 'estado', 'dependencia_principal', 'creado_por', 'creado_en')
    list_filter = ('eje', 'estado')
    search_fields = ('numero_control', 'titulo', 'descripcion')
    readonly_fields = ('creado_en', 'actualizado_en')


@admin.register(MensajeReporteCiudadano)
class MensajeReporteCiudadanoAdmin(admin.ModelAdmin):
    list_display = ('reporte', 'tipo_autor', 'autor_nombre', 'creado_en')
    list_filter = ('tipo_autor',)
    search_fields = ('contenido', 'autor_nombre')
