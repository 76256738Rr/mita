from django.core.management.base import BaseCommand

from conocimiento.models import Disciplina, FuenteInformacion
from core.seed_data import (
    CAPAS_GEO, CRUCES_INTER, DISCIPLINAS, EJES_ACCION, EJES_MITA,
    FUENTES, INDICADORES, INICIATIVA_LEY, LECCIONES, PERFILES_SNII,
    PROCESO_OPERATIVO, PROYECTO, PUNTOS_ATENCION_EDOMEX, SABERES, ZONAS_GEO,
)
from geoespacial.models import CapaGeografica, PuntoAtencionEdomex, ZonaGeografica
from interculturalidad.models import SaberTradicional
from legislacion.models import IniciativaLegislativa
from mita_engine.models import CruceInterdisciplinario, EjeMITA, PasoProceso
from proyectos.models import EjeAccion, LeccionAprendida, ProyectoReferencia
from reportes.models import IndicadorImpacto
from sni.models import PerfilSNI


class Command(BaseCommand):
    help = 'Carga datos semilla de la Plataforma MITA'

    def handle(self, *args, **options):
        self.stdout.write('Cargando datos semilla MITA...')

        for item in DISCIPLINAS:
            Disciplina.objects.update_or_create(slug=item['slug'], defaults=item)

        for item in ZONAS_GEO:
            ZonaGeografica.objects.update_or_create(slug=item['slug'], defaults=item)

        for item in CAPAS_GEO:
            CapaGeografica.objects.update_or_create(slug=item['slug'], defaults=item)

        for item in PUNTOS_ATENCION_EDOMEX:
            PuntoAtencionEdomex.objects.update_or_create(slug=item['slug'], defaults=item)

        from core.centros_salud_edomex import CENTROS_SALUD_EDOMEX
        PuntoAtencionEdomex.objects.filter(eje='salud').delete()
        for item in CENTROS_SALUD_EDOMEX:
            PuntoAtencionEdomex.objects.update_or_create(slug=item['slug'], defaults=item)

        for item in EJES_MITA:
            EjeMITA.objects.update_or_create(slug=item['slug'], defaults=item)

        for item in PROCESO_OPERATIVO:
            PasoProceso.objects.update_or_create(paso=item['paso'], defaults={
                'nombre': item['nombre'],
                'descripcion': item['descripcion'],
            })

        CruceInterdisciplinario.objects.all().delete()
        for item in CRUCES_INTER:
            CruceInterdisciplinario.objects.create(**item)

        proyecto, _ = ProyectoReferencia.objects.update_or_create(
            slug=PROYECTO['slug'],
            defaults={
                'nombre': PROYECTO['nombre'],
                'objetivo': PROYECTO['objetivo'],
                'enfoque': PROYECTO['enfoque'],
                'analogia': PROYECTO['analogia'],
                'metas_globales': PROYECTO['metas_globales'],
                'indicadores': PROYECTO['indicadores'],
            },
        )

        for item in EJES_ACCION:
            EjeAccion.objects.update_or_create(
                proyecto=proyecto,
                numero=item['numero'],
                defaults={
                    'nombre': item['nombre'],
                    'origen': item['origen'],
                    'acciones': item['acciones'],
                    'meta': item['meta'],
                },
            )

        for item in PERFILES_SNII:
            PerfilSNI.objects.update_or_create(titulo=item['titulo'], defaults=item)

        for item in FUENTES:
            FuenteInformacion.objects.update_or_create(nombre=item['nombre'], defaults=item)

        for item in SABERES:
            SaberTradicional.objects.update_or_create(titulo=item['titulo'], defaults=item)

        for item in LECCIONES:
            LeccionAprendida.objects.update_or_create(titulo=item['titulo'], defaults=item)

        for item in INDICADORES:
            IndicadorImpacto.objects.update_or_create(
                sector=item['sector'],
                nombre=item['nombre'],
                defaults=item,
            )

        IniciativaLegislativa.objects.update_or_create(
            titulo=INICIATIVA_LEY['titulo'],
            defaults=INICIATIVA_LEY,
        )

        from core.demo_simulation import crear_usuarios_demo, simular_proyecto_demo, simular_reporte_ciudadano_demo

        usuarios = crear_usuarios_demo()
        self.stdout.write(self.style.SUCCESS('Usuarios demo creados/actualizados (contraseña: mita2026)'))

        resultado = simular_proyecto_demo(usuarios)
        reporte_ciudadano = simular_reporte_ciudadano_demo(usuarios)
        self.stdout.write(self.style.SUCCESS(
            f"Proyecto demo simulado:\n"
            f"  • Activo (paso 6): {resultado['activo'].folio}\n"
            f"  • Dictaminado: {resultado['dictaminado'].folio}\n"
            f"  • Evaluación: {resultado['evaluacion']['puntuacion_total']}/100"
        ))
        if reporte_ciudadano:
            self.stdout.write(self.style.SUCCESS(
                f"  • Reporte ciudadano demo: {reporte_ciudadano.numero_control}"
            ))

        self.stdout.write(self.style.SUCCESS('Datos semilla cargados correctamente.'))
