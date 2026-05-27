from django.db import models


class SaberTradicional(models.Model):
    """Base de saberes tradicionales validados (RF-04)."""

    class Comunidad(models.TextChoices):
        MAZAHUA = 'mazahua', 'Mazahua'
        OTOMI = 'otomi', 'Otomí'
        NAHUATL = 'nahuatl', 'Náhuatl'
        MIXTECO = 'mixteco', 'Mixteco'
        OTRO = 'otro', 'Otro'

    titulo = models.CharField(max_length=300)
    comunidad = models.CharField(max_length=20, choices=Comunidad.choices)
    descripcion = models.TextField()
    aplicacion_salud = models.TextField()
    validado = models.BooleanField(default=True)
    fuente = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Saber tradicional'
        verbose_name_plural = 'Saberes tradicionales'
        ordering = ['comunidad', 'titulo']

    def __str__(self):
        return f'{self.titulo} ({self.get_comunidad_display()})'

    def to_dict(self):
        return {
            'id': self.pk,
            'titulo': self.titulo,
            'comunidad': self.comunidad,
            'comunidad_display': self.get_comunidad_display(),
            'descripcion': self.descripcion,
            'aplicacion_salud': self.aplicacion_salud,
            'validado': self.validado,
        }
