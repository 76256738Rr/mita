"""Motor de workflow MITA — orquestación de procesos y flujos."""

from datetime import timedelta

from django.core.files.base import ContentFile
from django.db import models, transaction
from django.utils import timezone

from core.models import RegistroAuditoria

from .models import Dictamen, Expediente, OpcionSolucion, PropuestaEvaluacion, TareaExpediente, TransicionExpediente
from .pdf import generar_pdf_dictamen
from .services import calcular_cruce, evaluar_analogia, generar_dictamen


PASOS = {
    1: {'nombre': 'Definición del asunto', 'rol': 'dependencia'},
    2: {'nombre': 'Recopilación de conocimiento', 'rol': 'analista'},
    3: {'nombre': 'Organización y relación', 'rol': 'analista'},
    4: {'nombre': 'Análisis y Analogía', 'rol': 'analista'},
    5: {'nombre': 'Generación de opciones', 'rol': 'analista'},
    6: {'nombre': 'Evaluación y selección', 'rol': 'investigador'},
    7: {'nombre': 'Dictamen de Validación', 'rol': 'admin'},
}

PLAZO_DIAS = 30


class WorkflowError(Exception):
    pass


class WorkflowEngine:
    """Orquesta el flujo completo registro → análisis → dictamen → seguimiento."""

    @staticmethod
    def generar_folio():
        count = Expediente.objects.count() + 1
        year = timezone.now().year
        return f'MITA-EXP-{year}-{count:05d}'

    @classmethod
    def crear_expediente(cls, usuario, titulo, descripcion='', solicitante='', dependencia=''):
        with transaction.atomic():
            expediente = Expediente.objects.create(
                folio=cls.generar_folio(),
                titulo=titulo,
                descripcion=descripcion,
                solicitante=solicitante or dependencia,
                dependencia=dependencia,
                creado_por=usuario if usuario.is_authenticated else None,
                responsable=usuario if usuario.is_authenticated else None,
                plazo_limite=timezone.now() + timedelta(days=PLAZO_DIAS),
                paso_actual=1,
                estado=Expediente.Estado.BORRADOR,
            )
            cls._registrar_transicion(
                expediente, None, 1, '', Expediente.Estado.BORRADOR,
                usuario, 'crear', 'Expediente registrado',
            )
            cls._crear_tarea(expediente, 1, 'Completar definición del asunto', 'dependencia')
            cls._auditar(usuario, 'CREAR_EXPEDIENTE', 'Expediente', expediente.folio)
        return expediente

    @classmethod
    def guardar_paso(cls, expediente, paso, datos, usuario):
        if paso != expediente.paso_actual:
            raise WorkflowError(f'El expediente está en el paso {expediente.paso_actual}, no en el {paso}.')

        artefactos = dict(expediente.artefactos or {})
        artefactos[str(paso)] = datos
        expediente.artefactos = artefactos

        if paso == 1:
            expediente.titulo = datos.get('titulo', expediente.titulo)
            expediente.descripcion = datos.get('descripcion', expediente.descripcion)
            expediente.solicitante = datos.get('solicitante', expediente.solicitante)
            expediente.dependencia = datos.get('dependencia', expediente.dependencia)
        elif paso == 2:
            expediente.disciplinas_ids = datos.get('disciplinas_ids', [])
        elif paso == 3:
            from conocimiento.models import Disciplina
            disciplinas_db = [d.to_dict() for d in Disciplina.objects.filter(slug__in=expediente.disciplinas_ids)]
            cruce = calcular_cruce(expediente.disciplinas_ids, disciplinas_db)
            artefactos['3'] = {**datos, 'cruce': cruce}
            if datos.get('zonas_ids'):
                from geoespacial.models import ZonaGeografica
                zonas = ZonaGeografica.objects.filter(slug__in=datos['zonas_ids'])
                artefactos['3']['zonas'] = [z.to_dict() for z in zonas]
            if datos.get('saberes_ids'):
                from interculturalidad.models import SaberTradicional
                saberes = SaberTradicional.objects.filter(pk__in=datos['saberes_ids'])
                artefactos['3']['saberes'] = [s.to_dict() for s in saberes]
            expediente.artefactos = artefactos
        elif paso == 4:
            evaluacion = evaluar_analogia(datos)
            expediente.evaluacion = evaluacion
            artefactos['4'] = {'criterios': datos, 'evaluacion': evaluacion}
            expediente.artefactos = artefactos
            cls._generar_opciones(expediente, evaluacion, datos)
        elif paso == 6:
            opcion_id = datos.get('opcion_id')
            if opcion_id:
                OpcionSolucion.objects.filter(expediente=expediente).update(seleccionada=False)
                OpcionSolucion.objects.filter(pk=opcion_id, expediente=expediente).update(seleccionada=True)

        expediente.save()
        cls._auditar(usuario, 'GUARDAR_PASO', 'Expediente', expediente.folio, {'paso': paso})
        return expediente

    @classmethod
    def avanzar(cls, expediente, usuario, comentario=''):
        paso = expediente.paso_actual
        cls._validar_paso(expediente, paso)

        if paso >= 7:
            raise WorkflowError('El expediente ya completó el flujo de dictamen.')

        paso_anterior = paso
        paso_nuevo = paso + 1
        estado_anterior = expediente.estado
        estado_nuevo = Expediente.Estado.EN_PROCESO if paso_nuevo < 7 else Expediente.Estado.PENDIENTE_REVISION

        if paso == 6:
            estado_nuevo = Expediente.Estado.PENDIENTE_REVISION

        with transaction.atomic():
            expediente.paso_actual = paso_nuevo
            expediente.estado = estado_nuevo
            expediente.save()

            TareaExpediente.objects.filter(expediente=expediente, paso=paso_anterior, completada=False).update(
                completada=True, completada_en=timezone.now(),
            )

            cls._registrar_transicion(
                expediente, paso_anterior, paso_nuevo,
                estado_anterior, estado_nuevo, usuario, 'avanzar', comentario,
            )

            if paso_nuevo <= 7 and estado_nuevo != Expediente.Estado.DICTAMINADO:
                info = PASOS[paso_nuevo]
                cls._crear_tarea(expediente, paso_nuevo, f"Completar: {info['nombre']}", info['rol'])

        cls._auditar(usuario, 'AVANZAR_PASO', 'Expediente', expediente.folio, {'paso': paso_nuevo})
        return expediente

    @classmethod
    def emitir_dictamen(cls, expediente, usuario):
        if expediente.paso_actual != 7:
            raise WorkflowError('Debe estar en el paso 7 para emitir el dictamen.')
        cls._validar_paso(expediente, 7)
        with transaction.atomic():
            cls._emitir_dictamen(expediente, usuario)
            expediente.estado = Expediente.Estado.DICTAMINADO
            expediente.save()
            cls._registrar_transicion(
                expediente, 7, 7, expediente.estado, Expediente.Estado.DICTAMINADO,
                usuario, 'dictaminar', 'Dictamen emitido',
            )
            TareaExpediente.objects.filter(expediente=expediente, paso=7, completada=False).update(
                completada=True, completada_en=timezone.now(),
            )
            cls._crear_tarea(expediente, 7, 'Seguimiento de impacto', 'analista', tipo='seguimiento')
        return expediente

    @classmethod
    def iniciar_seguimiento(cls, expediente, usuario, notas=''):
        if expediente.estado != Expediente.Estado.DICTAMINADO:
            raise WorkflowError('Solo expedientes dictaminados pueden pasar a seguimiento.')
        with transaction.atomic():
            expediente.estado = Expediente.Estado.EN_SEGUIMIENTO
            expediente.save()
            cls._registrar_transicion(
                expediente, 7, 7, Expediente.Estado.DICTAMINADO,
                Expediente.Estado.EN_SEGUIMIENTO, usuario, 'seguimiento', notas,
            )
        return expediente

    @classmethod
    def bandeja(cls, usuario=None):
        qs = TareaExpediente.objects.filter(completada=False).select_related(
            'expediente', 'asignado_a',
        ).order_by('vencimiento', '-prioridad')

        if usuario and usuario.is_authenticated:
            from core.permissions import obtener_rol
            rol = obtener_rol(usuario)
            qs = qs.filter(
                models.Q(asignado_a=usuario) | models.Q(rol_requerido=rol) | models.Q(rol_requerido='')
            )
        return qs

    @classmethod
    def historial(cls, expediente):
        return expediente.transiciones.select_related('usuario').all()

    @classmethod
    def _validar_paso(cls, expediente, paso):
        if paso == 1:
            if not expediente.titulo.strip():
                raise WorkflowError('El título es obligatorio.')
        elif paso == 2:
            if len(expediente.disciplinas_ids or []) < 2:
                raise WorkflowError('Seleccione al menos 2 disciplinas.')
        elif paso == 3:
            cruce = (expediente.artefactos or {}).get('3', {}).get('cruce')
            if not cruce or cruce.get('error'):
                raise WorkflowError('Debe calcular el cruce interdisciplinario.')
        elif paso == 4:
            if not expediente.evaluacion:
                raise WorkflowError('Debe completar la evaluación analógica.')
        elif paso == 5:
            if not expediente.opciones.exists():
                raise WorkflowError('Debe existir al menos una opción de solución.')
        elif paso == 6:
            if not expediente.opciones.filter(seleccionada=True).exists():
                raise WorkflowError('Debe seleccionar una opción de solución.')
        elif paso == 7:
            if hasattr(expediente, 'propuesta') and expediente.propuesta and hasattr(expediente.propuesta, 'dictamen'):
                return
            if not expediente.evaluacion:
                raise WorkflowError('Falta evaluación para emitir dictamen.')

    @classmethod
    def _emitir_dictamen(cls, expediente, usuario):
        artefacto = (expediente.artefactos or {}).get('4', {})
        criterios = artefacto.get('criterios', {})
        if not criterios:
            criterios = {
                'titulo': expediente.titulo,
                'descripcion': expediente.descripcion,
                'solicitante': expediente.solicitante,
            }
        criterios.setdefault('titulo', expediente.titulo)
        criterios.setdefault('descripcion', expediente.descripcion)
        criterios.setdefault('solicitante', expediente.solicitante)

        evaluacion = expediente.evaluacion or evaluar_analogia(criterios)
        dictamen_data = generar_dictamen(criterios, evaluacion, expediente.solicitante)

        propuesta = expediente.propuesta
        if not propuesta:
            propuesta = PropuestaEvaluacion.objects.create(
                titulo=expediente.titulo,
                descripcion=expediente.descripcion,
                solicitante=expediente.solicitante,
                estado=PropuestaEvaluacion.Estado.DICTAMINADO,
                criterios=criterios,
                puntuacion_total=evaluacion['puntuacion_total'],
                aprobado=evaluacion['aprobado'],
                creado_por=usuario if usuario and usuario.is_authenticated else expediente.creado_por,
            )
            expediente.propuesta = propuesta
        else:
            propuesta.estado = PropuestaEvaluacion.Estado.DICTAMINADO
            propuesta.criterios = criterios
            propuesta.puntuacion_total = evaluacion['puntuacion_total']
            propuesta.aprobado = evaluacion['aprobado']
            propuesta.save()

        dictamen_obj, created = Dictamen.objects.get_or_create(
            propuesta=propuesta,
            defaults={
                'folio': dictamen_data['folio'],
                'resultado': dictamen_data['resultado'],
                'puntuacion': dictamen_data['puntuacion'],
                'nivel_fronesis': dictamen_data['nivel_fronesis'],
                'evaluacion_completa': {'evaluacion': evaluacion, 'dictamen': dictamen_data},
            },
        )
        if created or not dictamen_obj.pdf_archivo:
            pdf_buffer = generar_pdf_dictamen(dictamen_data)
            dictamen_obj.pdf_archivo.save(
                f"{dictamen_data['folio']}.pdf",
                ContentFile(pdf_buffer.read()),
                save=True,
            )

        artefactos = dict(expediente.artefactos or {})
        artefactos['7'] = {'dictamen_folio': dictamen_data['folio'], 'dictamen_id': dictamen_obj.pk}
        expediente.artefactos = artefactos
        expediente.save()

    @classmethod
    def _generar_opciones(cls, expediente, evaluacion, criterios):
        OpcionSolucion.objects.filter(expediente=expediente).delete()
        base_score = evaluacion['puntuacion_total']
        opciones_data = [
            {
                'titulo': 'Opción integral recomendada',
                'descripcion': 'Implementación sistémica con los ejes de acción seleccionados y adaptación cultural.',
                'puntuacion': min(100, base_score + 5),
                'fundamento': 'Mayor coherencia sistémica según evaluación MITA.',
            },
            {
                'titulo': 'Opción gradual por territorio',
                'descripcion': 'Despliegue por fases en hotspots del Corredor Oriente y zonas indígenas.',
                'puntuacion': base_score,
                'fundamento': 'Reduce riesgo operativo y permite aprendizaje iterativo.',
            },
            {
                'titulo': 'Opción mínima viable',
                'descripcion': 'Intervención focalizada en detección y control glucémico.',
                'puntuacion': max(40, base_score - 15),
                'fundamento': 'Menor costo pero impacto limitado en determinantes sociales.',
            },
        ]
        for i, op in enumerate(opciones_data, 1):
            OpcionSolucion.objects.create(expediente=expediente, orden=i, **op)

    @classmethod
    def _crear_tarea(cls, expediente, paso, titulo, rol, tipo='completar_paso'):
        TareaExpediente.objects.create(
            expediente=expediente,
            paso=paso,
            tipo=tipo,
            titulo=titulo,
            rol_requerido=rol,
            vencimiento=expediente.plazo_limite,
            prioridad=8 if paso >= 6 else 5,
        )

    @classmethod
    def _registrar_transicion(cls, expediente, paso_ant, paso_nuevo, est_ant, est_nuevo, usuario, accion, comentario):
        TransicionExpediente.objects.create(
            expediente=expediente,
            paso_anterior=paso_ant,
            paso_nuevo=paso_nuevo,
            estado_anterior=est_ant or '',
            estado_nuevo=est_nuevo,
            usuario=usuario if usuario and usuario.is_authenticated else None,
            accion=accion,
            comentario=comentario,
        )

    @classmethod
    def _auditar(cls, usuario, accion, entidad, entidad_id, detalle=None):
        RegistroAuditoria.objects.create(
            usuario=usuario if usuario and usuario.is_authenticated else None,
            accion=accion,
            entidad=entidad,
            entidad_id=str(entidad_id),
            detalle=detalle or {},
        )
