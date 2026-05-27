from django.db import models


class IniciativaLegislativa(models.Model):
    """Iniciativas de reforma normativa (RF-10)."""

    titulo = models.CharField(max_length=300)
    descripcion = models.TextField()
    articulos = models.JSONField(default=list)
    estado = models.CharField(max_length=50, default='propuesta')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Iniciativa legislativa'
        verbose_name_plural = 'Iniciativas legislativas'

    def __str__(self):
        return self.titulo
