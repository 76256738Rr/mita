from django.conf import settings
from django.db import models


class PerfilUsuario(models.Model):
    """Perfil extendido con roles granulares (RF seguridad)."""

    class Rol(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        ANALISTA = 'analista', 'Analista MITA'
        INVESTIGADOR = 'investigador', 'Investigador SNI'
        DEPENDENCIA = 'dependencia', 'Dependencia Gubernamental'
        AUDITOR = 'auditor', 'Auditor'
        PUBLICO = 'publico', 'Público General'

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_mita',
    )
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.ANALISTA)
    dependencia = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return f'{self.usuario.username} ({self.get_rol_display()})'


class RegistroAuditoria(models.Model):
    """Trazabilidad y auditoría (RF-08)."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    accion = models.CharField(max_length=100)
    entidad = models.CharField(max_length=100)
    entidad_id = models.CharField(max_length=100, blank=True)
    detalle = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de auditoría'
        verbose_name_plural = 'Registros de auditoría'
        ordering = ['-creado_en']

    def __str__(self):
        return f'{self.accion} — {self.entidad} ({self.creado_en:%Y-%m-%d %H:%M})'


class ReporteCiudadano(models.Model):
    """Reporte de problemática ciudadana por eje temático."""

    class Estado(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        RECIBIDO = 'recibido', 'Recibido'
        EN_REVISION = 'en_revision', 'En revisión'
        TURNADO = 'turnado', 'Turnado a dependencia'
        EN_ATENCION = 'en_atencion', 'En atención'
        RESUELTO = 'resuelto', 'Resuelto'
        NO_PROCEDE = 'no_procede', 'No procede'

    class Eje(models.TextChoices):
        SALUD = 'salud', 'Salud'
        EDUCACION = 'educacion', 'Educación'
        CORRUPCION = 'corrupcion', 'Corrupción'
        ECONOMIA = 'economia', 'Economía'
        EMPLEO = 'empleo', 'Empleo'
        SEGURIDAD = 'seguridad', 'Seguridad'

    numero_control = models.CharField(max_length=30, unique=True, db_index=True)
    eje = models.CharField(max_length=20, choices=Eje.choices)
    titulo = models.CharField(max_length=300)
    descripcion = models.TextField()
    datos_captura = models.JSONField(default=dict, blank=True)
    municipio = models.CharField(max_length=120, blank=True)
    dependencia_principal = models.CharField(max_length=200)
    dependencias_involucradas = models.JSONField(default=list, blank=True)
    ruta_tramite = models.JSONField(default=list, blank=True)
    responsable_atencion = models.JSONField(default=dict, blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.RECIBIDO)
    respuesta_dependencia = models.TextField(blank=True)
    fecha_estimada_atencion = models.DateField(null=True, blank=True)
    motivo_no_procede = models.TextField(blank=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reportes_ciudadanos',
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reporte ciudadano'
        verbose_name_plural = 'Reportes ciudadanos'
        ordering = ['-creado_en']

    def __str__(self):
        return f'{self.numero_control} — {self.get_eje_display()}'

    @property
    def eje_config(self):
        from core.ciudadania_config import get_eje_config
        return get_eje_config(self.eje)

    @property
    def paso_activo(self):
        for paso in self.ruta_tramite or []:
            if paso.get('estado') == 'activo':
                return paso
        return None

    @property
    def responsable_actual(self):
        if self.responsable_atencion:
            return self.responsable_atencion
        paso = self.paso_activo
        if paso and paso.get('responsable'):
            return paso['responsable']
        return {}


class MensajeReporteCiudadano(models.Model):
    """Mensajes del chat ciudadano — IA, dependencia o sistema."""

    class TipoAutor(models.TextChoices):
        CIUDADANO = 'ciudadano', 'Ciudadano'
        IA = 'ia', 'Asistente IA MITA'
        DEPENDENCIA = 'dependencia', 'Dependencia'
        RESPONSABLE = 'responsable', 'Responsable de atención'
        SISTEMA = 'sistema', 'Sistema'

    reporte = models.ForeignKey(
        ReporteCiudadano,
        on_delete=models.CASCADE,
        related_name='mensajes',
        null=True,
        blank=True,
    )
    sesion_key = models.CharField(max_length=64, blank=True, db_index=True)
    tipo_autor = models.CharField(max_length=20, choices=TipoAutor.choices)
    autor_nombre = models.CharField(max_length=120)
    contenido = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mensaje de reporte'
        verbose_name_plural = 'Mensajes de reportes'
        ordering = ['creado_en']

    def __str__(self):
        return f'{self.autor_nombre}: {self.contenido[:50]}'
