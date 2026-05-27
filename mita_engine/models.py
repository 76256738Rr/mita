from django.conf import settings
from django.db import models


class EjeMITA(models.Model):
    """Los 5 ejes de la metodología MITA."""

    slug = models.SlugField(unique=True)
    nombre = models.CharField(max_length=100)
    sigla = models.CharField(max_length=5)
    descripcion = models.TextField()
    proposito = models.TextField()
    fuentes = models.JSONField(default=list)

    class Meta:
        verbose_name = 'Eje MITA'
        verbose_name_plural = 'Ejes MITA'
        ordering = ['id']

    def __str__(self):
        return self.nombre

    def to_dict(self):
        return {
            'id': self.slug,
            'nombre': self.nombre,
            'sigla': self.sigla,
            'descripcion': self.descripcion,
            'proposito': self.proposito,
            'fuentes': self.fuentes,
        }


class PasoProceso(models.Model):
    """Proceso operativo MITA (7 pasos)."""

    paso = models.PositiveSmallIntegerField(unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()

    class Meta:
        verbose_name = 'Paso del proceso'
        verbose_name_plural = 'Pasos del proceso'
        ordering = ['paso']

    def __str__(self):
        return f'Paso {self.paso}: {self.nombre}'

    def to_dict(self):
        return {
            'paso': self.paso,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
        }


class CruceInterdisciplinario(models.Model):
    """Cruces y sinergias predefinidos (RF-03)."""

    disciplinas_texto = models.JSONField(default=list)
    concepto = models.CharField(max_length=200)
    resultado = models.TextField()

    class Meta:
        verbose_name = 'Cruce interdisciplinario'
        verbose_name_plural = 'Cruces interdisciplinarios'

    def __str__(self):
        return self.concepto

    def to_dict(self):
        return {
            'id': self.pk,
            'disciplinas': self.disciplinas_texto,
            'concepto': self.concepto,
            'resultado': self.resultado,
        }


class PropuestaEvaluacion(models.Model):
    """Propuesta sometida a evaluación analógica (RF-06, RF-08)."""

    class Estado(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        EN_ANALISIS = 'en_analisis', 'En análisis'
        DICTAMINADO = 'dictaminado', 'Dictaminado'
        SEGUIMIENTO = 'seguimiento', 'En seguimiento'

    titulo = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True)
    solicitante = models.CharField(max_length=200, blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.BORRADOR)
    criterios = models.JSONField(default=dict)
    puntuacion_total = models.FloatField(null=True, blank=True)
    aprobado = models.BooleanField(null=True, blank=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Propuesta de evaluación'
        verbose_name_plural = 'Propuestas de evaluación'
        ordering = ['-creado_en']

    def __str__(self):
        return self.titulo


class Dictamen(models.Model):
    """Dictamen de Validación Obligatorio (RF-06, RF-08)."""

    propuesta = models.OneToOneField(
        PropuestaEvaluacion,
        on_delete=models.CASCADE,
        related_name='dictamen',
    )
    folio = models.CharField(max_length=50, unique=True)
    resultado = models.CharField(max_length=30)
    puntuacion = models.FloatField()
    nivel_fronesis = models.BooleanField(default=False)
    evaluacion_completa = models.JSONField(default=dict)
    pdf_archivo = models.FileField(upload_to='dictamenes/', blank=True)
    emitido_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Dictamen MITA'
        verbose_name_plural = 'Dictámenes MITA'
        ordering = ['-emitido_en']

    def __str__(self):
        return self.folio


class Expediente(models.Model):
    """Instancia de proceso MITA — flujo completo RF-08."""

    class Estado(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        EN_PROCESO = 'en_proceso', 'En proceso'
        PENDIENTE_REVISION = 'pendiente_revision', 'Pendiente de revisión'
        DICTAMINADO = 'dictaminado', 'Dictaminado'
        EN_SEGUIMIENTO = 'en_seguimiento', 'En seguimiento'
        CERRADO = 'cerrado', 'Cerrado'
        CANCELADO = 'cancelado', 'Cancelado'

    folio = models.CharField(max_length=30, unique=True)
    titulo = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True)
    solicitante = models.CharField(max_length=200, blank=True)
    dependencia = models.CharField(max_length=200, blank=True)
    paso_actual = models.PositiveSmallIntegerField(default=1)
    estado = models.CharField(max_length=25, choices=Estado.choices, default=Estado.BORRADOR)
    propuesta = models.OneToOneField(
        PropuestaEvaluacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expediente',
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expedientes_responsable',
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expedientes_creados',
    )
    plazo_limite = models.DateTimeField(null=True, blank=True)
    disciplinas_ids = models.JSONField(default=list, blank=True)
    evaluacion = models.JSONField(null=True, blank=True)
    artefactos = models.JSONField(default=dict, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Expediente MITA'
        verbose_name_plural = 'Expedientes MITA'
        ordering = ['-actualizado_en']

    def __str__(self):
        return f'{self.folio} — {self.titulo}'

    @property
    def paso_nombre(self):
        from mita_engine.workflow import PASOS
        return PASOS.get(self.paso_actual, {}).get('nombre', f'Paso {self.paso_actual}')

    @property
    def progreso_pct(self):
        return round((self.paso_actual / 7) * 100)

    @property
    def vencido(self):
        if self.plazo_limite and self.estado not in (
            self.Estado.DICTAMINADO, self.Estado.CERRADO, self.Estado.CANCELADO,
        ):
            from django.utils import timezone
            return timezone.now() > self.plazo_limite
        return False

    def to_dict(self):
        return {
            'id': self.pk,
            'folio': self.folio,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'paso_actual': self.paso_actual,
            'paso_nombre': self.paso_nombre,
            'estado': self.estado,
            'estado_display': self.get_estado_display(),
            'progreso_pct': self.progreso_pct,
            'plazo_limite': self.plazo_limite.isoformat() if self.plazo_limite else None,
            'vencido': self.vencido,
        }


class TransicionExpediente(models.Model):
    """Historial de transiciones del flujo."""

    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE, related_name='transiciones')
    paso_anterior = models.PositiveSmallIntegerField(null=True, blank=True)
    paso_nuevo = models.PositiveSmallIntegerField()
    estado_anterior = models.CharField(max_length=25, blank=True)
    estado_nuevo = models.CharField(max_length=25)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
    )
    accion = models.CharField(max_length=50)
    comentario = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Transición de expediente'
        verbose_name_plural = 'Transiciones de expediente'
        ordering = ['creado_en']

    def __str__(self):
        return f'{self.expediente.folio}: paso {self.paso_anterior} → {self.paso_nuevo}'


class TareaExpediente(models.Model):
    """Tareas asignables en la bandeja de trabajo."""

    class Tipo(models.TextChoices):
        COMPLETAR_PASO = 'completar_paso', 'Completar paso'
        REVISAR = 'revisar', 'Revisar'
        FIRMAR = 'firmar', 'Firmar dictamen'
        SEGUIMIENTO = 'seguimiento', 'Seguimiento'

    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE, related_name='tareas')
    paso = models.PositiveSmallIntegerField()
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.COMPLETAR_PASO)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    asignado_a = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tareas_mita',
    )
    rol_requerido = models.CharField(max_length=20, blank=True)
    completada = models.BooleanField(default=False)
    prioridad = models.PositiveSmallIntegerField(default=5)
    vencimiento = models.DateTimeField(null=True, blank=True)
    completada_en = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tarea de expediente'
        verbose_name_plural = 'Tareas de expediente'
        ordering = ['-prioridad', 'vencimiento']

    def __str__(self):
        return f'{self.expediente.folio} — {self.titulo}'

    @property
    def urgente(self):
        if self.vencimiento:
            from django.utils import timezone
            return timezone.now() > self.vencimiento
        return False


class OpcionSolucion(models.Model):
    """Opciones de solución — pasos 5 y 6."""

    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE, related_name='opciones')
    titulo = models.CharField(max_length=300)
    descripcion = models.TextField()
    puntuacion = models.FloatField(default=0)
    fundamento = models.TextField(blank=True)
    seleccionada = models.BooleanField(default=False)
    orden = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'Opción de solución'
        verbose_name_plural = 'Opciones de solución'
        ordering = ['orden']

    def __str__(self):
        return self.titulo
