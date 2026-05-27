"""Utilidades del proceso operativo integrado."""

from django.db.models import Count

from mita_engine.models import CruceInterdisciplinario, Expediente, PasoProceso
from mita_engine.proceso_config import PROCESO_OPERATIVO, get_paso_config
from mita_engine.workflow import WorkflowEngine, WorkflowError


def paso_esta_completo(expediente, paso):
    """Determina si un paso del proceso operativo está completo para un expediente."""
    if paso > expediente.paso_actual:
        return False
    if paso < expediente.paso_actual:
        return True
    try:
        WorkflowEngine._validar_paso(expediente, paso)
        return True
    except WorkflowError:
        return False


def estado_proceso_expediente(expediente):
    """Estado de los 7 pasos para un expediente."""
    pasos_db = {p.paso: p for p in PasoProceso.objects.all()}
    resultado = []
    for num in range(1, 8):
        cfg = get_paso_config(num)
        db = pasos_db.get(num)
        completo = paso_esta_completo(expediente, num)
        activo = expediente.paso_actual == num
        resultado.append({
            'paso': num,
            'nombre': db.nombre if db else cfg.get('nombre', f'Paso {num}'),
            'descripcion': db.descripcion if db else cfg.get('descripcion', ''),
            'modulo': cfg.get('modulo', ''),
            'rf': cfg.get('rf', ''),
            'rol': cfg.get('rol', ''),
            'herramientas': cfg.get('herramientas', []),
            'acciones': cfg.get('acciones', []),
            'resultado': cfg.get('resultado', ''),
            'completo': completo,
            'activo': activo,
            'pendiente': num > expediente.paso_actual,
        })
    return resultado


def metricas_proceso_operativo():
    """Métricas globales del proceso operativo para el hub."""
    por_paso = (
        Expediente.objects
        .exclude(estado__in=[Expediente.Estado.CERRADO, Expediente.Estado.CANCELADO])
        .values('paso_actual')
        .annotate(total=Count('id'))
    )
    conteo = {item['paso_actual']: item['total'] for item in por_paso}
    pasos_db = list(PasoProceso.objects.all())
    pasos = []
    for num in range(1, 8):
        cfg = get_paso_config(num)
        db = next((p for p in pasos_db if p.paso == num), None)
        expedientes_paso = Expediente.objects.filter(paso_actual=num).exclude(
            estado__in=[Expediente.Estado.CERRADO, Expediente.Estado.CANCELADO],
        ).order_by('-actualizado_en')[:5]
        pasos.append({
            'paso': num,
            'nombre': db.nombre if db else cfg['nombre'],
            'descripcion': db.descripcion if db else cfg['descripcion'],
            'modulo': cfg['modulo'],
            'rf': cfg['rf'],
            'rol': cfg['rol'],
            'url_name': cfg.get('url_name', ''),
            'herramientas': cfg.get('herramientas', []),
            'acciones': cfg.get('acciones', []),
            'resultado': cfg.get('resultado', ''),
            'expedientes_count': conteo.get(num, 0),
            'expedientes': list(expedientes_paso),
        })
    return {
        'pasos': pasos,
        'total_activos': Expediente.objects.exclude(
            estado__in=[Expediente.Estado.CERRADO, Expediente.Estado.CANCELADO],
        ).count(),
        'total_dictaminados': Expediente.objects.filter(
            estado__in=[Expediente.Estado.DICTAMINADO, Expediente.Estado.EN_SEGUIMIENTO],
        ).count(),
        'cruces_disponibles': CruceInterdisciplinario.objects.count(),
    }


def contexto_herramientas(expediente, paso):
    """Enlaces contextuales a módulos de la plataforma para el paso actual."""
    cfg = get_paso_config(paso)
    links = []
    for tool in cfg.get('herramientas', []):
        url_map = {
            'base-datos': ('base-datos', 'Base de Conocimiento'),
            'mapa': ('mapa', 'Mapa Geoespacial'),
            'metodologia': ('metodologia', 'Metodología MITA'),
            'analogia': ('analogia', 'Motor Analógico'),
            'proyecto': ('proyecto', 'Proyecto de Referencia'),
            'sni': ('sni', 'Perfiles SNI'),
            'dictamenes': ('dictamenes', 'Dictámenes'),
            'reportes': ('reportes', 'Indicadores de Impacto'),
            'interculturalidad': ('base-datos', 'Saberes tradicionales'),
        }
        if tool in url_map:
            name, label = url_map[tool]
            links.append({'name': name, 'label': label, 'tool': tool})
    return {
        'config': cfg,
        'links': links,
        'acciones': cfg.get('acciones', []),
        'resultado_esperado': cfg.get('resultado', ''),
    }
