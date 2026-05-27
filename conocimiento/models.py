from django.db import models


class Disciplina(models.Model):
    """Base de conocimiento multidisciplinario (RF-01, RF-02)."""

    slug = models.SlugField(unique=True)
    nombre = models.CharField(max_length=150)
    grupo = models.CharField(max_length=50)
    area = models.CharField(max_length=100)
    aportacion = models.TextField()
    dato_clave = models.TextField()
    fuente = models.CharField(max_length=200)
    nivel_confiabilidad = models.PositiveSmallIntegerField(default=85)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Disciplina'
        verbose_name_plural = 'Disciplinas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def to_dict(self):
        return {
            'id': self.slug,
            'nombre': self.nombre,
            'grupo': self.grupo,
            'area': self.area,
            'aportacion': self.aportacion,
            'dato_clave': self.dato_clave,
            'fuente': self.fuente,
            'nivel_confiabilidad': self.nivel_confiabilidad,
        }


class FuenteInformacion(models.Model):
    """Fuentes oficiales validadas (RF-01)."""

    class TipoFuente(models.TextChoices):
        GUBERNAMENTAL = 'gubernamental', 'Gubernamental'
        ACADEMICA = 'academica', 'Académica'
        INTERNACIONAL = 'internacional', 'Internacional'
        TRADICIONAL = 'tradicional', 'Saberes tradicionales'

    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TipoFuente.choices)
    url_api = models.URLField(blank=True)
    nivel_confiabilidad = models.PositiveSmallIntegerField(default=80)
    activa = models.BooleanField(default=True)
    ultima_sincronizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Fuente de información'
        verbose_name_plural = 'Fuentes de información'

    def __str__(self):
        return self.nombre
