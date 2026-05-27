from django.db import models


class ProyectoReferencia(models.Model):
    """Proyecto de referencia del sistema (caso diabetes Edomex)."""

    slug = models.SlugField(unique=True, default='edomex-diabetes')
    nombre = models.CharField(max_length=300)
    objetivo = models.TextField()
    enfoque = models.TextField()
    analogia = models.JSONField(default=dict)
    metas_globales = models.JSONField(default=dict)
    indicadores = models.JSONField(default=dict)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Proyecto de referencia'
        verbose_name_plural = 'Proyectos de referencia'

    def __str__(self):
        return self.nombre


class EjeAccion(models.Model):
    """Ejes de acción del proyecto de referencia."""

    proyecto = models.ForeignKey(
        ProyectoReferencia,
        on_delete=models.CASCADE,
        related_name='ejes_accion',
    )
    numero = models.PositiveSmallIntegerField()
    nombre = models.CharField(max_length=200)
    origen = models.CharField(max_length=200)
    acciones = models.JSONField(default=list)
    meta = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Eje de acción'
        verbose_name_plural = 'Ejes de acción'
        ordering = ['numero']
        unique_together = [('proyecto', 'numero')]

    def __str__(self):
        return f'Eje {self.numero}: {self.nombre}'

    def to_dict(self):
        return {
            'id': self.numero,
            'nombre': self.nombre,
            'origen': self.origen,
            'acciones': self.acciones,
            'meta': self.meta,
        }


class LeccionAprendida(models.Model):
    """Lecciones aprendidas de proyectos sociales previos (RF-06 integración SNI)."""

    class Sector(models.TextChoices):
        SALUD = 'salud', 'Salud'
        EDUCACION = 'educacion', 'Educación'
        DESARROLLO = 'desarrollo', 'Desarrollo Social'

    titulo = models.CharField(max_length=300)
    sector = models.CharField(max_length=20, choices=Sector.choices)
    institucion = models.CharField(max_length=200)
    descripcion = models.TextField()
    impacto_medido = models.CharField(max_length=200, blank=True)
    anio = models.PositiveSmallIntegerField(default=2024)

    class Meta:
        verbose_name = 'Lección aprendida'
        verbose_name_plural = 'Lecciones aprendidas'
        ordering = ['-anio']

    def __str__(self):
        return self.titulo
