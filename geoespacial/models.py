from django.db import models


class ZonaGeografica(models.Model):
    """Zonas geográficas y hotspots (RF-07)."""

    class TipoZona(models.TextChoices):
        HOTSPOT = 'hotspot', 'Hotspot'
        MEDIA = 'media', 'Media'
        BAJA = 'baja', 'Baja'

    class Corredor(models.TextChoices):
        ORIENTE = 'oriente', 'Corredor Oriente'
        CONURBADA = 'conurbada', 'Zona Conurbada'
        INDIGENA = 'indigena', 'Región Indígena'
        PONIENTE = 'poniente', 'Norte y Poniente'

    slug = models.SlugField(unique=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TipoZona.choices)
    corredor = models.CharField(max_length=20, choices=Corredor.choices)
    lat = models.FloatField()
    lng = models.FloatField()
    prevalencia = models.FloatField()
    mortalidad = models.FloatField()
    pobreza = models.CharField(max_length=20)
    descripcion = models.TextField()

    class Meta:
        verbose_name = 'Zona geográfica'
        verbose_name_plural = 'Zonas geográficas'
        ordering = ['-prevalencia']

    def __str__(self):
        return self.nombre

    def to_dict(self):
        return {
            'id': self.slug,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'corredor': self.corredor,
            'lat': self.lat,
            'lng': self.lng,
            'prevalencia': self.prevalencia,
            'mortalidad': self.mortalidad,
            'pobreza': self.pobreza,
            'descripcion': self.descripcion,
        }


class CapaGeografica(models.Model):
    """Capas SIG (RF-07)."""

    slug = models.SlugField(unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    class Meta:
        verbose_name = 'Capa geográfica'
        verbose_name_plural = 'Capas geográficas'

    def __str__(self):
        return self.nombre

    def to_dict(self):
        return {
            'id': self.slug,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
        }


class PuntoAtencionEdomex(models.Model):
    """Puntos de atención ciudadana en el Estado de México por eje temático."""

    class Eje(models.TextChoices):
        SALUD = 'salud', 'Salud'
        EDUCACION = 'educacion', 'Educación'
        EMPLEO = 'empleo', 'Empleo'
        SEGURIDAD = 'seguridad', 'Seguridad'
        ECONOMIA = 'economia', 'Economía'
        CORRUPCION = 'corrupcion', 'Corrupción'

    slug = models.SlugField(unique=True)
    nombre = models.CharField(max_length=200)
    eje = models.CharField(max_length=20, choices=Eje.choices)
    tipo = models.CharField(max_length=80)
    municipio = models.CharField(max_length=100)
    lat = models.FloatField()
    lng = models.FloatField()
    direccion = models.CharField(max_length=300)
    telefono = models.CharField(max_length=40, blank=True)
    horario = models.CharField(max_length=120, blank=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Punto de atención Edomex'
        verbose_name_plural = 'Puntos de atención Edomex'
        ordering = ['eje', 'municipio', 'nombre']

    def __str__(self):
        return f'{self.nombre} ({self.municipio})'

    def to_dict(self):
        return {
            'slug': self.slug,
            'nombre': self.nombre,
            'eje': self.eje,
            'tipo': self.tipo,
            'municipio': self.municipio,
            'lat': self.lat,
            'lng': self.lng,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'horario': self.horario,
            'descripcion': self.descripcion,
        }
