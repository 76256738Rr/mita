"""Configuración del proceso operativo MITA — vincula cada paso con módulos de la plataforma."""

PROCESO_OPERATIVO = {
    1: {
        'nombre': 'Definición del asunto',
        'descripcion': 'Se identifica claramente qué problema, necesidad o proyecto se va a analizar.',
        'modulo': 'Expedientes',
        'rf': 'RF-08',
        'rol': 'dependencia',
        'url_name': 'expediente-nuevo',
        'herramientas': [],
        'acciones': [
            'Registrar título y descripción del asunto',
            'Identificar solicitante y dependencia',
            'Establecer plazo de atención (30 días)',
        ],
        'resultado': 'Expediente MITA creado con folio único',
    },
    2: {
        'nombre': 'Recopilación de conocimiento',
        'descripcion': 'El sistema accede a toda la información válida relacionada con el tema.',
        'modulo': 'Base de Conocimiento',
        'rf': 'RF-01',
        'rol': 'analista',
        'url_name': 'base-datos',
        'herramientas': ['base-datos', 'buscar'],
        'acciones': [
            'Consultar disciplinas validadas (SEDESA, INEGI, SNI, CECyTEM)',
            'Seleccionar al menos 2 áreas del saber',
            'Verificar nivel de confiabilidad de fuentes',
        ],
        'resultado': 'Disciplinas vinculadas al expediente',
    },
    3: {
        'nombre': 'Organización y relación',
        'descripcion': 'Se ordenan los datos y se establecen conexiones entre áreas del saber.',
        'modulo': 'Interdisciplina + Geoespacial',
        'rf': 'RF-03',
        'rol': 'analista',
        'url_name': 'mapa',
        'herramientas': ['metodologia', 'mapa', 'interculturalidad'],
        'acciones': [
            'Calcular cruce interdisciplinario',
            'Identificar sinergias y contradicciones',
            'Contextualizar territorialmente (hotspots SIG)',
            'Integrar saberes tradicionales validados',
        ],
        'resultado': 'Mapa conceptual y cruce documentado',
    },
    4: {
        'nombre': 'Análisis y Analogía',
        'descripcion': 'Se aplican algoritmos para medir, comparar y evaluar contra parámetros de calidad, ley y realidad.',
        'modulo': 'Motor Analógico',
        'rf': 'RF-06',
        'rol': 'analista',
        'url_name': 'analogia',
        'herramientas': ['analogia'],
        'acciones': [
            'Evaluar legalidad, viabilidad y pertinencia',
            'Detectar riesgos (sesgado, radical, divagante)',
            'Calcular puntuación analógica MITA',
        ],
        'resultado': 'Evaluación analógica con criterios ponderados',
    },
    5: {
        'nombre': 'Generación de opciones',
        'descripcion': 'El sistema presenta alternativas de solución fundamentadas y viables.',
        'modulo': 'Transdisciplina',
        'rf': 'RF-05',
        'rol': 'analista',
        'url_name': 'proyecto',
        'herramientas': ['proyecto'],
        'acciones': [
            'Generar opciones a partir de la evaluación',
            'Contrastar con proyecto de referencia',
            'Documentar fundamentos de cada alternativa',
        ],
        'resultado': 'Opciones de solución comparables',
    },
    6: {
        'nombre': 'Evaluación y selección',
        'descripcion': 'Se analizan las opciones y se determina la más adecuada con respaldo técnico y legal.',
        'modulo': 'SNI + Legislación',
        'rf': 'RF-02 / RF-10',
        'rol': 'investigador',
        'url_name': 'sni',
        'herramientas': ['sni', 'legislacion'],
        'acciones': [
            'Seleccionar la opción más viable',
            'Vincular perfiles SNI recomendados',
            'Verificar compatibilidad normativa',
        ],
        'resultado': 'Opción seleccionada con respaldo',
    },
    7: {
        'nombre': 'Dictamen de Validación',
        'descripcion': 'Se emite el documento oficial que certifica que la acción es correcta, válida y segura.',
        'modulo': 'Dictámenes + Reportes',
        'rf': 'RF-08 / RF-11',
        'rol': 'admin',
        'url_name': 'dictamenes',
        'herramientas': ['dictamenes', 'reportes'],
        'acciones': [
            'Emitir Dictamen de Validación MITA (PDF)',
            'Registrar trazabilidad y auditoría',
            'Iniciar seguimiento de indicadores de impacto',
        ],
        'resultado': 'Dictamen obligatorio + seguimiento post-emisión',
    },
}


def get_paso_config(numero):
    return PROCESO_OPERATIVO.get(numero, {})


def herramientas_paso(numero):
    cfg = get_paso_config(numero)
    return cfg.get('herramientas', [])
