"""Utilidades del Motor Analógico MITA (RF-06)."""

from django.core.files.base import ContentFile

from mita_engine.models import Dictamen, PropuestaEvaluacion
from mita_engine.pdf import generar_pdf_dictamen
from mita_engine.services import generar_dictamen


CAMPOS_CHECKBOX = [
    'marco_legal', 'derechos_humanos', 'normativa_aplicable',
    'recursos_tecnicos', 'infraestructura', 'plazo_ejecucion',
    'retorno_inversion', 'sostenibilidad', 'beneficiarios',
    'necesidad_identificada', 'impacto_esperado', 'enfoque_integral',
    'adaptacion_cultural', 'interculturalidad',
]

CRITERIOS_LABELS = {
    'legalidad': 'Legalidad',
    'viabilidad_tecnica': 'Viabilidad técnica',
    'viabilidad_financiera': 'Viabilidad financiera',
    'pertinencia_social': 'Pertinencia social',
    'coherencia_sistemica': 'Coherencia sistémica',
    'adaptacion_cultural': 'Adaptación cultural',
}

CRITERIO_ICONOS = {
    'legalidad': 'img/analogia/criterio-legalidad.svg',
    'viabilidad_tecnica': 'img/analogia/criterio-viabilidad.svg',
    'viabilidad_financiera': 'img/analogia/criterio-viabilidad.svg',
    'pertinencia_social': 'img/analogia/criterio-pertinencia.svg',
    'coherencia_sistemica': 'img/analogia/criterio-coherencia.svg',
    'adaptacion_cultural': 'img/analogia/criterio-cultural.svg',
}

RIESGO_ICONOS = {
    'sesgado': 'img/analogia/riesgo-sesgado.svg',
    'radical': 'img/analogia/riesgo-radical.svg',
    'divagante': 'img/analogia/riesgo-divagante.svg',
    'cultural': 'img/analogia/riesgo-cultural.svg',
}


def propuesta_desde_post(post):
    """Convierte datos del formulario POST a dict de propuesta."""
    ejes = post.getlist('ejes_accion')
    return {
        'titulo': post.get('titulo', '').strip(),
        'descripcion': post.get('descripcion', '').strip(),
        'solicitante': post.get('solicitante', '').strip(),
        'presupuesto': float(post.get('presupuesto') or 0),
        'ejes_accion': [int(x) for x in ejes if str(x).isdigit()],
        **{campo: bool(post.get(campo)) for campo in CAMPOS_CHECKBOX},
    }


def persistir_dictamen(propuesta, evaluacion, usuario=None):
    """Guarda propuesta, dictamen y PDF en base de datos."""
    dictamen_data = generar_dictamen(propuesta, evaluacion, propuesta.get('solicitante', ''))

    propuesta_obj = PropuestaEvaluacion.objects.create(
        titulo=propuesta['titulo'],
        descripcion=propuesta.get('descripcion', ''),
        solicitante=propuesta.get('solicitante', ''),
        estado=PropuestaEvaluacion.Estado.DICTAMINADO,
        criterios=propuesta,
        puntuacion_total=evaluacion['puntuacion_total'],
        aprobado=evaluacion['aprobado'],
        creado_por=usuario if usuario and usuario.is_authenticated else None,
    )

    pdf_buffer = generar_pdf_dictamen(dictamen_data)
    dictamen_obj = Dictamen.objects.create(
        propuesta=propuesta_obj,
        folio=dictamen_data['folio'],
        resultado=dictamen_data['resultado'],
        puntuacion=dictamen_data['puntuacion'],
        nivel_fronesis=dictamen_data['nivel_fronesis'],
        evaluacion_completa={'evaluacion': evaluacion, 'dictamen': dictamen_data},
    )
    dictamen_obj.pdf_archivo.save(
        f"{dictamen_data['folio']}.pdf",
        ContentFile(pdf_buffer.read()),
        save=True,
    )
    return dictamen_data, dictamen_obj
