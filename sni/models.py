from django.db import models


class PerfilSNI(models.Model):
    """Perfiles SNI recomendados (RF-02, integración SNI)."""

    titulo = models.CharField(max_length=300)
    area = models.CharField(max_length=150)
    nivel = models.CharField(max_length=50)
    funcion = models.TextField()
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Perfil SNI'
        verbose_name_plural = 'Perfiles SNI'

    def __str__(self):
        return self.titulo

    def to_dict(self):
        return {
            'id': self.pk,
            'titulo': self.titulo,
            'area': self.area,
            'nivel': self.nivel,
            'funcion': self.funcion,
        }


class InvestigadorSNI(models.Model):
    """Base de investigadores SNI para vinculación."""

    nombre = models.CharField(max_length=200)
    perfil = models.ForeignKey(
        PerfilSNI,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='investigadores',
    )
    area_especialidad = models.CharField(max_length=200)
    nivel_snii = models.CharField(max_length=20)
    institucion = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    disponible = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Investigador SNI'
        verbose_name_plural = 'Investigadores SNI'

    def __str__(self):
        return self.nombre
