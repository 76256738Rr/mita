"""Navegación lateral por rol de usuario."""

from django.urls import reverse


MENU_CIUDADANO = [
    {
        'id': 'ciudadania-portal',
        'label': '🏛 Ventanilla Ciudadana',
        'url_name': 'ciudadania-portal',
        'active_exact': ('/ciudadania/',),
    },
    {
        'id': 'ciudadania-nuevo',
        'label': '➕ Registrar problemática',
        'url_name': 'ciudadania-nuevo',
        'active_prefixes': ('/ciudadania/nuevo',),
    },
    {
        'id': 'ciudadania-workflow',
        'label': '🔀 Ruta gráfica de atención',
        'url_name': 'ciudadania-workflow',
        'active_prefixes': ('/ciudadania/ruta-grafica',),
    },
]

MENU_INSTITUCIONAL = [
    {
        'id': 'dashboard',
        'label': '📊 Dashboard',
        'url_name': 'dashboard',
        'roles': {'admin', 'analista', 'investigador', 'dependencia', 'auditor'},
        'active_exact': ('/',),
    },
    {
        'id': 'bandeja',
        'label': '📥 Bandeja de trabajo',
        'url_name': 'bandeja',
        'roles': {'admin', 'analista', 'investigador', 'dependencia'},
        'active_prefixes': ('/bandeja',),
    },
    {
        'id': 'expedientes',
        'label': '📁 Expedientes',
        'url_name': 'expedientes',
        'roles': {'admin', 'analista', 'investigador', 'dependencia', 'auditor'},
        'active_prefixes': ('/expedientes',),
        'active_exclude_prefixes': ('/expedientes/nuevo',),
    },
    {
        'id': 'expediente-nuevo',
        'label': '➕ Registrar asunto',
        'url_name': 'expediente-nuevo',
        'roles': {'admin', 'dependencia'},
        'active_prefixes': ('/expedientes/nuevo',),
    },
    {
        'id': 'base-datos',
        'label': '🧠 Base de Conocimiento',
        'url_name': 'base-datos',
        'roles': {'admin', 'analista'},
        'active_prefixes': ('/base-datos',),
    },
    {
        'id': 'mapa',
        'label': '🗺️ Mapa Geoespacial',
        'url_name': 'mapa',
        'roles': {'admin', 'analista'},
        'active_prefixes': ('/mapa',),
    },
    {
        'id': 'proceso',
        'label': '⚙️ Proceso Operativo',
        'url_name': 'proceso',
        'roles': {'admin', 'analista', 'investigador', 'dependencia'},
        'active_prefixes': ('/proceso',),
    },
    {
        'id': 'metodologia',
        'label': '📚 Metodología MITA',
        'url_name': 'metodologia',
        'roles': {'admin', 'analista', 'investigador'},
        'active_prefixes': ('/metodologia',),
    },
    {
        'id': 'proyecto',
        'label': '🚀 Proyecto Demo',
        'url_name': 'proyecto',
        'roles': {'admin', 'analista'},
        'active_prefixes': ('/proyecto',),
    },
    {
        'id': 'analogia',
        'label': '🔬 Motor Analógico',
        'url_name': 'analogia',
        'roles': {'admin', 'analista'},
        'active_prefixes': ('/analogia',),
    },
    {
        'id': 'dictamenes',
        'label': '⚖️ Dictámenes',
        'url_name': 'dictamenes',
        'roles': {'admin', 'investigador', 'auditor'},
        'active_prefixes': ('/dictamenes',),
    },
    {
        'id': 'sni',
        'label': '👨‍🔬 Perfiles SNI',
        'url_name': 'sni',
        'roles': {'admin', 'investigador'},
        'active_prefixes': ('/sni',),
    },
    {
        'id': 'reportes',
        'label': '📈 Reportes',
        'url_name': 'reportes',
        'roles': {'admin', 'auditor'},
        'active_prefixes': ('/reportes',),
    },
    {
        'id': 'admin',
        'label': '🔐 Administración',
        'href': '/admin/',
        'roles': {'admin'},
        'active_prefixes': ('/admin',),
    },
]


def _es_activo(item, path):
    for excl in item.get('active_exclude_prefixes', ()):
        if path.startswith(excl):
            return False
    exact = item.get('active_exact')
    if exact is not None:
        return path in exact
    for prefix in item.get('active_prefixes', ()):
        if path.startswith(prefix):
            return True
    return False


def menu_para_rol(rol, path='/'):
    """Ítems de menú visibles para el rol, con URL y estado activo."""
    if rol == 'publico':
        fuente = MENU_CIUDADANO
    else:
        fuente = [i for i in MENU_INSTITUCIONAL if rol in i.get('roles', set())]

    items = []
    for raw in fuente:
        item = dict(raw)
        item['url'] = raw.get('href') or reverse(raw['url_name'])
        item['active'] = _es_activo(raw, path)
        items.append(item)
    return items
