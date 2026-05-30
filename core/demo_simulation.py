"""Simulación del proyecto demo EDOMEX DIABETES y usuarios por rol."""

from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from core.models import PerfilUsuario
from core.seed_data import PROYECTO
from mita_engine.models import CruceInterdisciplinario, Expediente, OpcionSolucion, TareaExpediente, TransicionExpediente
from mita_engine.services import calcular_cruce, evaluar_analogia
from mita_engine.workflow import WorkflowEngine

DEMO_FOLIO_ACTIVO = 'MITA-DEMO-2026-ACTIVO'
DEMO_FOLIO_DICTAMINADO = 'MITA-DEMO-2026-DICTAMINADO'
PASSWORD_DEMO = 'mita2026'

USUARIOS_DEMO = [
    {
        'username': 'dependencia',
        'rol': PerfilUsuario.Rol.DEPENDENCIA,
        'rol_label': 'Dependencia Gubernamental',
        'nombre': 'María González',
        'dependencia': 'SEDESA — Secretaría de Salud',
        'descripcion': 'Registra iniciativas y completa el Paso 1 (Definición del asunto).',
        'paso_sugerido': 1,
        'color': '#3182ce',
    },
    {
        'username': 'analista',
        'rol': PerfilUsuario.Rol.ANALISTA,
        'rol_label': 'Analista MITA',
        'nombre': 'Carlos Mendoza',
        'dependencia': 'Coordinación MITA — SEDESA',
        'descripcion': 'Recopila conocimiento, cruces interdisciplinarios y evaluación analógica (Pasos 2–5).',
        'paso_sugerido': 4,
        'color': '#2c5282',
    },
    {
        'username': 'investigador',
        'rol': PerfilUsuario.Rol.INVESTIGADOR,
        'rol_label': 'Investigador SNI',
        'nombre': 'Dra. Edith Castañeda',
        'dependencia': 'CECyTEM / SNI Nivel II',
        'descripcion': 'Evalúa y selecciona la opción de solución más viable (Paso 6).',
        'paso_sugerido': 6,
        'color': '#276749',
    },
    {
        'username': 'admin',
        'rol': PerfilUsuario.Rol.ADMIN,
        'rol_label': 'Administrador',
        'nombre': 'Juan de Dios Escalante',
        'dependencia': 'Dirección General MITA',
        'descripcion': 'Emite el Dictamen de Validación MITA y autoriza seguimiento (Paso 7).',
        'paso_sugerido': 7,
        'color': '#1a365d',
    },
    {
        'username': 'auditor',
        'rol': PerfilUsuario.Rol.AUDITOR,
        'rol_label': 'Auditor',
        'nombre': 'Lic. Patricia Ruiz',
        'dependencia': 'Contraloría del Estado de México',
        'descripcion': 'Consulta trazabilidad, dictámenes e indicadores de impacto (solo lectura).',
        'paso_sugerido': 0,
        'color': '#718096',
    },
    {
        'username': 'ciudadano',
        'rol': PerfilUsuario.Rol.PUBLICO,
        'rol_label': 'Público General',
        'nombre': 'Roberto Hernández',
        'dependencia': 'Ciudadano del Estado de México',
        'descripcion': 'Registra problemáticas por eje temático con asistente IA, número de control y chat con dependencias.',
        'paso_sugerido': 0,
        'color': '#38a169',
    },
]

DISCIPLINAS_DEMO = [
    'sedesa', 'antropologia', 'sociologia', 'pedagogia', 'economia_salud',
    'tecnologia_alimentaria', 'informatica', 'ingenieria_urbana', 'cecyctem',
]

ZONAS_DEMO = ['ecatepec', 'nezahualcoyotl', 'chalco', 'valle_chalco', 'san_felipe']

CRITERIOS_DEMO = {
    'titulo': PROYECTO['nombre'],
    'descripcion': (
        f"{PROYECTO['objetivo']}. {PROYECTO['enfoque']} "
        'Intervención integral en Corredor Oriente y regiones indígenas mazahua-otomí.'
    ),
    'solicitante': 'SEDESA — Gobierno del Estado de México',
    'marco_legal': True,
    'derechos_humanos': True,
    'normativa_aplicable': True,
    'recursos_tecnicos': True,
    'infraestructura': True,
    'plazo_ejecucion': True,
    'presupuesto': 2_500_000_000,
    'retorno_inversion': True,
    'sostenibilidad': True,
    'beneficiarios': True,
    'necesidad_identificada': True,
    'impacto_esperado': True,
    'enfoque_integral': True,
    'adaptacion_cultural': True,
    'interculturalidad': True,
    'ejes_accion': [1, 2, 3, 4, 5, 6],
}


def crear_usuarios_demo():
    """Crea o actualiza los 5 usuarios demo con sus perfiles."""
    usuarios = {}
    for data in USUARIOS_DEMO:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': f"{data['username']}@mita.edomex.gob.mx",
                'first_name': data['nombre'].split()[0],
                'last_name': ' '.join(data['nombre'].split()[1:]) if len(data['nombre'].split()) > 1 else '',
                'is_staff': data['rol'] in (PerfilUsuario.Rol.ADMIN, PerfilUsuario.Rol.ANALISTA),
                'is_superuser': data['rol'] == PerfilUsuario.Rol.ADMIN,
            },
        )
        if created or not user.check_password(PASSWORD_DEMO):
            user.set_password(PASSWORD_DEMO)
            user.save()
        perfil, _ = PerfilUsuario.objects.update_or_create(
            usuario=user,
            defaults={'rol': data['rol'], 'dependencia': data['dependencia']},
        )
        usuarios[data['username']] = user
    return usuarios


def _artefactos_pasos_1_5(cruces_pks, saberes_pks):
    from conocimiento.models import Disciplina
    from geoespacial.models import ZonaGeografica
    from interculturalidad.models import SaberTradicional

    disciplinas_db = [d.to_dict() for d in Disciplina.objects.filter(slug__in=DISCIPLINAS_DEMO)]
    cruce = calcular_cruce(DISCIPLINAS_DEMO, disciplinas_db)
    evaluacion = evaluar_analogia(CRITERIOS_DEMO)
    zonas = ZonaGeografica.objects.filter(slug__in=ZONAS_DEMO)
    saberes = SaberTradicional.objects.filter(pk__in=saberes_pks)

    return {
        '1': {
            'titulo': PROYECTO['nombre'],
            'descripcion': CRITERIOS_DEMO['descripcion'],
            'solicitante': 'SEDESA',
            'dependencia': 'Secretaría de Salud del Estado de México',
        },
        '2': {'disciplinas_ids': DISCIPLINAS_DEMO},
        '3': {
            'confirmado': True,
            'zonas_ids': ZONAS_DEMO,
            'saberes_ids': list(saberes_pks),
            'cruces_catalogo': [str(pk) for pk in cruces_pks],
            'cruce': cruce,
            'zonas': [z.to_dict() for z in zonas],
            'saberes': [s.to_dict() for s in saberes],
        },
        '4': {'criterios': CRITERIOS_DEMO, 'evaluacion': evaluacion},
        '5': {'generado': True, 'opciones_count': 3},
    }, evaluacion


def simular_proyecto_demo(usuarios=None):
    """
    Simula el proyecto EDOMEX DIABETES dentro de la plataforma:
    - Expediente ACTIVO en paso 6 (listo para selección por investigador)
    - Expediente DICTAMINADO en seguimiento (para auditoría y reportes)
    """
    if usuarios is None:
        usuarios = crear_usuarios_demo()

    dependencia = usuarios.get('dependencia') or usuarios.get('analista')
    analista = usuarios.get('analista')
    investigador = usuarios.get('investigador')
    admin = usuarios.get('admin')

    cruces_pks = list(CruceInterdisciplinario.objects.values_list('pk', flat=True)[:3])
    from interculturalidad.models import SaberTradicional
    saberes_pks = list(SaberTradicional.objects.values_list('pk', flat=True))

    artefactos, evaluacion = _artefactos_pasos_1_5(cruces_pks, saberes_pks)
    plazo = timezone.now() + timedelta(days=30)

    # --- Expediente activo (paso 6) ---
    activo, _ = Expediente.objects.update_or_create(
        folio=DEMO_FOLIO_ACTIVO,
        defaults={
            'titulo': PROYECTO['nombre'],
            'descripcion': CRITERIOS_DEMO['descripcion'],
            'solicitante': 'SEDESA',
            'dependencia': 'Secretaría de Salud del Estado de México',
            'paso_actual': 6,
            'estado': Expediente.Estado.EN_PROCESO,
            'creado_por': dependencia,
            'responsable': investigador,
            'plazo_limite': plazo,
            'disciplinas_ids': DISCIPLINAS_DEMO,
            'evaluacion': evaluacion,
            'artefactos': artefactos,
        },
    )

    OpcionSolucion.objects.filter(expediente=activo).delete()
    WorkflowEngine._generar_opciones(activo, evaluacion, CRITERIOS_DEMO)

    TareaExpediente.objects.filter(expediente=activo).delete()
    TransicionExpediente.objects.filter(expediente=activo).delete()
    transiciones = [
        (None, 1, '', Expediente.Estado.BORRADOR, 'crear', 'Proyecto demo EDOMEX DIABETES registrado'),
        (1, 2, Expediente.Estado.BORRADOR, Expediente.Estado.EN_PROCESO, 'avanzar', 'Definición completada'),
        (2, 3, Expediente.Estado.EN_PROCESO, Expediente.Estado.EN_PROCESO, 'avanzar', '9 disciplinas vinculadas'),
        (3, 4, Expediente.Estado.EN_PROCESO, Expediente.Estado.EN_PROCESO, 'avanzar', 'Cruce interdisciplinario calculado'),
        (4, 5, Expediente.Estado.EN_PROCESO, Expediente.Estado.EN_PROCESO, 'avanzar', f"Evaluación analógica: {evaluacion['puntuacion_total']}/100"),
        (5, 6, Expediente.Estado.EN_PROCESO, Expediente.Estado.EN_PROCESO, 'avanzar', '3 opciones de solución generadas'),
    ]
    for paso_ant, paso_nuevo, est_ant, est_nuevo, accion, comentario in transiciones:
        TransicionExpediente.objects.create(
            expediente=activo,
            paso_anterior=paso_ant,
            paso_nuevo=paso_nuevo,
            estado_anterior=est_ant or '',
            estado_nuevo=est_nuevo,
            usuario=analista,
            accion=accion,
            comentario=comentario,
        )
    TareaExpediente.objects.create(
        expediente=activo,
        paso=6,
        tipo='completar_paso',
        titulo='Seleccionar opción de solución — Proyecto demo',
        rol_requerido='investigador',
        vencimiento=plazo,
        prioridad=8,
    )

    # --- Expediente dictaminado (seguimiento) ---
    dictaminado, _ = Expediente.objects.update_or_create(
        folio=DEMO_FOLIO_DICTAMINADO,
        defaults={
            'titulo': f"[REFERENCIA] {PROYECTO['nombre']}",
            'descripcion': 'Expediente demo completado — dictamen emitido y en seguimiento de impacto.',
            'solicitante': 'SEDESA',
            'dependencia': 'Secretaría de Salud del Estado de México',
            'paso_actual': 7,
            'estado': Expediente.Estado.EN_SEGUIMIENTO,
            'creado_por': dependencia,
            'responsable': admin,
            'plazo_limite': plazo,
            'disciplinas_ids': DISCIPLINAS_DEMO,
            'evaluacion': evaluacion,
            'artefactos': {**artefactos, '6': {'opcion_seleccionada': 'Opción integral recomendada'}},
        },
    )

    OpcionSolucion.objects.filter(expediente=dictaminado).delete()
    WorkflowEngine._generar_opciones(dictaminado, evaluacion, CRITERIOS_DEMO)
    primera = dictaminado.opciones.first()
    if primera:
        OpcionSolucion.objects.filter(expediente=dictaminado).update(seleccionada=False)
        primera.seleccionada = True
        primera.save()

    if dictaminado.propuesta_id:
        try:
            dictaminado.propuesta.dictamen.delete()
        except Exception:
            pass
        dictaminado.propuesta.delete()
        dictaminado.propuesta = None

    dictaminado.paso_actual = 7
    dictaminado.estado = Expediente.Estado.PENDIENTE_REVISION
    dictaminado.save()

    try:
        WorkflowEngine.emitir_dictamen(dictaminado, admin)
        dictaminado.refresh_from_db()
        WorkflowEngine.iniciar_seguimiento(
            dictaminado, admin,
            'Seguimiento demo: metas -20% prevalencia, +40% control glucémico, -25% mortalidad.',
        )
    except Exception:
        pass

    return {'activo': activo, 'dictaminado': dictaminado, 'evaluacion': evaluacion}


def simular_reporte_ciudadano_demo(usuarios):
    """Crea un reporte ciudadano demo para el usuario público."""
    from core.ciudadania_services import crear_reporte_ciudadano
    from core.models import ReporteCiudadano

    ciudadano = usuarios.get('ciudadano')
    if not ciudadano:
        return None

    folio_demo = 'MITA-CIU-DEMO-00001'
    ReporteCiudadano.objects.filter(numero_control=folio_demo).delete()

    datos = {
        'nombre_completo': 'Roberto Hernández García',
        'celular': '5512345678',
        'correo': 'roberto.hernandez@correo.demo',
        'municipio': 'Ecatepec',
        'tipo_enfermedad': 'Diabetes mellitus tipo 2',
        'medicamentos': ['Insulina NPH', 'Metformina', 'Glucómetro'],
        'tipo_atencion': 'Medicamentos',
        'descripcion_problema': (
            'No me entregan insulina en el centro de salud de Ecatepec desde hace 3 semanas. '
            'Soy paciente con diabetes tipo 2 y necesito continuidad en mi tratamiento.'
        ),
        'centro_salud': 'hg-ecatepec-americas',
        'centro_salud_nombre': 'Hospital General Ecatepec Las Américas',
        'centro_salud_direccion': 'Av. Las Américas s/n, San Cristóbal Centro, Ecatepec',
        'tiene_seguro': 'Sí — IMSS-Bienestar',
        'urgencia': 'Alta',
    }

    reporte = crear_reporte_ciudadano(
        ciudadano,
        'salud',
        'Salud — Diabetes mellitus tipo 2',
        datos['descripcion_problema'],
        datos,
        'Ecatepec',
        numero_control=folio_demo,
    )
    from core.ciudadania_services import enriquecer_ruta_demo, registrar_mensaje
    from core.models import MensajeReporteCiudadano

    enriquecer_ruta_demo(reporte, dias_atras=3)
    responsable = reporte.responsable_atencion or {}
    registrar_mensaje(
        reporte=reporte,
        tipo_autor=MensajeReporteCiudadano.TipoAutor.RESPONSABLE,
        autor_nombre=responsable.get('nombre', 'Enlace ciudadano'),
        contenido=(
            f'**{responsable.get("nombre", "Enlace")}:** He verificado su expediente con el '
            f'Hospital General Ecatepec Las Américas. Estamos gestionando el surtimiento de insulina. '
            f'Le mantendré informado por este chat.'
        ),
        metadata={'responsable': responsable},
    )
    return reporte
