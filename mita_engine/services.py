"""Motor de algoritmos MITA: interdisciplina, analogía y dictamen."""

from datetime import datetime
import hashlib
import uuid


def calcular_cruce(disciplina_ids, disciplinas_db):
    """Genera conexiones interdisciplinarias entre disciplinas seleccionadas."""
    seleccionadas = [d for d in disciplinas_db if d['id'] in disciplina_ids]
    if len(seleccionadas) < 2:
        return {'error': 'Se requieren al menos 2 disciplinas para el cruce interdisciplinario'}

    nombres = [d['nombre'] for d in seleccionadas]
    conceptos = [d['aportacion'] for d in seleccionadas]
    areas = set(d['area'] for d in seleccionadas)
    complementariedad = min(100, len(areas) * 25 + len(seleccionadas) * 10)

    return {
        'disciplinas': nombres,
        'concepto_cruzado': ' + '.join(conceptos[:2]),
        'areas_involucradas': list(areas),
        'complementariedad': complementariedad,
        'sintesis': (
            f"El cruce entre {' y '.join(nombres)} revela un sistema causal integrado "
            f"donde {seleccionadas[0]['dato_clave']}. "
            f'La intervención debe abordar {len(areas)} dimensiones simultáneamente.'
        ),
        'datos_clave': [d['dato_clave'] for d in seleccionadas],
    }


def evaluar_analogia(propuesta):
    """Algoritmo analógico MITA: evalúa coherencia, legalidad, viabilidad y pertinencia."""
    criterios = {
        'legalidad': _evaluar_legalidad(propuesta),
        'viabilidad_tecnica': _evaluar_viabilidad(propuesta),
        'viabilidad_financiera': _evaluar_financiera(propuesta),
        'pertinencia_social': _evaluar_pertinencia(propuesta),
        'coherencia_sistemica': _evaluar_coherencia(propuesta),
        'adaptacion_cultural': _evaluar_cultural(propuesta),
    }

    pesos = {
        'legalidad': 0.20,
        'viabilidad_tecnica': 0.15,
        'viabilidad_financiera': 0.15,
        'pertinencia_social': 0.20,
        'coherencia_sistemica': 0.20,
        'adaptacion_cultural': 0.10,
    }

    puntuacion_total = sum(criterios[k] * pesos[k] for k in criterios)
    aprobado = puntuacion_total >= 70

    recomendaciones = []
    for criterio, valor in criterios.items():
        if valor < 70:
            recomendaciones.append(_recomendacion(criterio, valor))

    riesgos = _detectar_riesgos(propuesta, criterios)

    return {
        'criterios': criterios,
        'puntuacion_total': round(puntuacion_total, 1),
        'aprobado': aprobado,
        'nivel': _nivel(puntuacion_total),
        'recomendaciones': recomendaciones,
        'fronesis': puntuacion_total >= 80,
        'riesgos': riesgos,
    }


def generar_dictamen(propuesta, evaluacion, solicitante=''):
    """Genera dictamen oficial de validación MITA."""
    folio = hashlib.sha256(
        f"{propuesta.get('titulo', '')}{datetime.now().isoformat()}".encode()
    ).hexdigest()[:12].upper()

    return {
        'folio': f'MITA-DV-{folio}',
        'fecha': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'tipo': 'Dictamen de Validación MITA',
        'solicitante': solicitante or 'Dependencia del Gobierno del Estado de México',
        'asunto': propuesta.get('titulo', 'Sin título'),
        'descripcion': propuesta.get('descripcion', ''),
        'resultado': 'APROBADO' if evaluacion['aprobado'] else 'REQUIERE AJUSTES',
        'puntuacion': evaluacion['puntuacion_total'],
        'nivel_fronesis': evaluacion['fronesis'],
        'criterios_evaluados': evaluacion['criterios'],
        'recomendaciones': evaluacion['recomendaciones'],
        'riesgos_detectados': evaluacion.get('riesgos', []),
        'certificaciones': [
            'Cumplimiento de la ley y derechos humanos'
            if evaluacion['criterios']['legalidad'] >= 70
            else 'Pendiente: revisión legal',
            'Utilidad real para la sociedad'
            if evaluacion['criterios']['pertinencia_social'] >= 70
            else 'Pendiente: validación social',
            'Viabilidad técnica, financiera y social'
            if evaluacion['aprobado']
            else 'Pendiente: ajustes de viabilidad',
            'Calidad y solidez de la propuesta'
            if evaluacion['criterios']['coherencia_sistemica'] >= 70
            else 'Pendiente: mayor coherencia sistémica',
        ],
        'validez': (
            'Este dictamen es requisito obligatorio para aprobación de programas, '
            'políticas y obras públicas.'
        ),
        'id': str(uuid.uuid4()),
    }


def sintesis_transdisciplinaria(disciplinas, cruces):
    """Síntesis integral de problemas (RF-05)."""
    return {
        'ciclo_causal': (
            'Desigualdad → Alimentación inadecuada + Falta de actividad → '
            'Sobrepeso/Obesidad → Diabetes → Complicaciones → '
            'Mayor pobreza → Peor salud'
        ),
        'conclusion': (
            "No es 'más médicos', ni 'más medicinas', ni 'más educación por separado'. "
            'Es reordenar todo el sistema social, cultural, urbano, educativo y económico '
            'alrededor de la salud, con acciones diferenciadas por territorio.'
        ),
        'disciplinas_integradas': len(disciplinas),
        'cruces_identificados': len(cruces),
        'riesgos_evitados': {
            'sesgado': 'Solo médicos → no resuelve',
            'radical': 'Soluciones millonarias, inaplicables',
            'divagante': 'Muchas ideas, ninguna ejecutable',
        },
    }


def comparar_cultural_cientifico(saber, enfoque_cientifico):
    """Comparador cultural-científico (RF-04)."""
    return {
        'saber_tradicional': saber,
        'enfoque_cientifico': enfoque_cientifico,
        'recomendacion': (
            'Integrar ambos enfoques con personal bilingüe, materiales adaptados '
            'y medicina tradicional complementaria a la alópata.'
        ),
        'impacto_esperado': 'Reducción del 35% en abandono en zonas indígenas',
    }


def analizar_impacto_normativo(propuesta):
    """Análisis de impacto normativo (RF-10)."""
    return {
        'marco_actual': 'Ley de Salud del Estado de México, Ley de Derechos de los Pueblos Indígenas',
        'brechas_detectadas': [
            'Falta de obligatoriedad del Dictamen MITA en iniciativas públicas',
            'Normativa insuficiente sobre etiquetado alimentario',
        ],
        'iniciativa_sugerida': {
            'titulo': 'Iniciativa de Ley de Obligatoriedad del Dictamen MITA',
            'articulos_clave': [
                'Art. 1: Toda iniciativa pública requiere Dictamen de Validación MITA',
                'Art. 2: Plazo máximo de emisión: 30 días hábiles',
                'Art. 3: Trazabilidad y auditoría obligatoria',
            ],
        },
        'compatibilidad': evaluar_analogia(propuesta)['criterios']['legalidad'],
    }


def _detectar_riesgos(propuesta, criterios):
    riesgos = []
    if criterios['coherencia_sistemica'] < 50:
        riesgos.append({'tipo': 'sesgado', 'descripcion': 'Enfoque parcial que no resuelve el problema sistémico'})
    if propuesta.get('presupuesto', 0) > 500_000_000 and criterios['viabilidad_financiera'] < 60:
        riesgos.append({'tipo': 'radical', 'descripcion': 'Solución de alto costo con viabilidad financiera limitada'})
    if len(propuesta.get('ejes_accion', [])) > 5 and criterios['coherencia_sistemica'] < 70:
        riesgos.append({'tipo': 'divagante', 'descripcion': 'Demasiadas acciones sin integración coherente'})
    if criterios['adaptacion_cultural'] < 50:
        riesgos.append({'tipo': 'cultural', 'descripcion': 'Riesgo de bajo apego en comunidades indígenas (60% abandono)'})
    return riesgos


def _evaluar_legalidad(p):
    base = 60.0
    if p.get('marco_legal'):
        base += 15
    if p.get('derechos_humanos'):
        base += 15
    if p.get('normativa_aplicable'):
        base += 10
    return min(100, base)


def _evaluar_viabilidad(p):
    base = 50.0
    if p.get('recursos_tecnicos'):
        base += 20
    if p.get('infraestructura'):
        base += 15
    if p.get('plazo_ejecucion'):
        base += 15
    return min(100, base)


def _evaluar_financiera(p):
    base = 50.0
    if p.get('presupuesto', 0) > 0:
        base += 20
    if p.get('retorno_inversion'):
        base += 15
    if p.get('sostenibilidad'):
        base += 15
    return min(100, base)


def _evaluar_pertinencia(p):
    base = 55.0
    if p.get('beneficiarios'):
        base += 15
    if p.get('necesidad_identificada'):
        base += 15
    if p.get('impacto_esperado'):
        base += 15
    return min(100, base)


def _evaluar_coherencia(p):
    base = 50.0
    ejes = p.get('ejes_accion', [])
    base += min(30, len(ejes) * 10)
    if p.get('enfoque_integral'):
        base += 20
    return min(100, base)


def _evaluar_cultural(p):
    base = 60.0
    if p.get('adaptacion_cultural'):
        base += 20
    if p.get('interculturalidad'):
        base += 20
    return min(100, base)


def _nivel(puntuacion):
    if puntuacion >= 90:
        return 'Excelente — Fronesis equilibrada'
    if puntuacion >= 80:
        return 'Muy bueno — Alta viabilidad'
    if puntuacion >= 70:
        return 'Aprobado — Viable con seguimiento'
    if puntuacion >= 50:
        return 'Requiere ajustes significativos'
    return 'No viable en condiciones actuales'


def _recomendacion(criterio, valor):
    msgs = {
        'legalidad': 'Fortalecer el marco legal y verificar cumplimiento de derechos humanos.',
        'viabilidad_tecnica': 'Detallar recursos técnicos e infraestructura necesaria.',
        'viabilidad_financiera': 'Presentar análisis costo-beneficio y fuentes de financiamiento.',
        'pertinencia_social': 'Validar con población beneficiaria y ajustar a necesidades reales.',
        'coherencia_sistemica': 'Integrar más ejes de acción para abordar el problema de forma integral.',
        'adaptacion_cultural': 'Incorporar adaptación intercultural y saberes comunitarios.',
    }
    label = criterio.replace('_', ' ').title()
    return f'[{label} ({valor:.0f}%)] {msgs.get(criterio, "Revisar criterio.")}'
