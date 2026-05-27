from django.db import models


class IndicadorImpacto(models.Model):
    """Indicadores de impacto por sector (RF-11)."""

    class Sector(models.TextChoices):
        SALUD = 'salud', 'Salud'
        EDUCACION = 'educacion', 'Educación'
        DESARROLLO = 'desarrollo', 'Desarrollo Social'
        URBANO = 'urbano', 'Urbano'
        ECONOMICO = 'economico', 'Económico'

    sector = models.CharField(max_length=20, choices=Sector.choices)
    nombre = models.CharField(max_length=200)
    valor_actual = models.FloatField()
    meta = models.FloatField()
    unidad = models.CharField(max_length=50)
    tendencia = models.CharField(max_length=20, default='estable')

    class Meta:
        verbose_name = 'Indicador de impacto'
        verbose_name_plural = 'Indicadores de impacto'
        ordering = ['sector', 'nombre']

    def __str__(self):
        return f'{self.get_sector_display()}: {self.nombre}'

    def to_dict(self):
        avance = round((self.valor_actual / self.meta * 100) if self.meta else 0, 1)
        return {
            'sector': self.sector,
            'nombre': self.nombre,
            'valor_actual': self.valor_actual,
            'meta': self.meta,
            'unidad': self.unidad,
            'tendencia': self.tendencia,
            'avance_pct': min(100, avance),
        }
