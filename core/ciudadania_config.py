"""Configuración de ejes, campos dinámicos y dependencias para reportes ciudadanos."""

from core.seed_data import MUNICIPIOS_EDOMEX

ENTIDAD = 'Estado de México'

CAMPOS_CONTACTO = [
    {'name': 'nombre_completo', 'label': 'Nombre completo', 'type': 'text', 'required': True},
    {'name': 'celular', 'label': 'Celular', 'type': 'tel', 'required': True},
    {'name': 'correo', 'label': 'Correo electrónico', 'type': 'email', 'required': True},
]

MUNICIPIO_EDOMEX = {
    'name': 'municipio',
    'label': 'Municipio (Estado de México)',
    'type': 'select',
    'required': True,
    'options': MUNICIPIOS_EDOMEX,
    'filtra_ubicaciones': True,
}

TIPOS_ENFERMEDAD = [
    'Diabetes mellitus tipo 2', 'Diabetes mellitus tipo 1', 'Hipertensión arterial',
    'Obesidad', 'Enfermedad renal crónica', 'Asma', 'COVID-19 / secuelas',
    'Cáncer', 'Depresión / ansiedad', 'Otra enfermedad crónica',
]

MEDICAMENTOS_SALUD = [
    'Metformina', 'Insulina NPH', 'Insulina Glargina', 'Glibenclamida', 'Sitagliptina',
    'Losartán', 'Enalapril', 'Amlodipino', 'Atorvastatina', 'Aspirina',
    'Paracetamol', 'Ibuprofeno', 'Omeprazol', 'Salbutamol', 'Otro medicamento',
]

ETIQUETAS_UBICACION = {
    'salud': 'Centros de salud y farmacias en Edomex',
    'educacion': 'Escuelas e instituciones educativas en Edomex',
    'empleo': 'Módulos de empleo y centros de capacitación en Edomex',
    'seguridad': 'Instancias de seguridad y denuncia en Edomex',
    'economia': 'Oficinas de apoyo económico en Edomex',
    'corrupcion': 'Instancias de denuncia anticorrupción en Edomex',
    'agua': 'Organismos de agua y puntos de atención en Edomex',
}
CAMPO_IMPACTO_SOCIAL = {
    'name': 'impacto_social',
    'label': '¿Qué tan grave considera el problema?',
    'type': 'select',
    'required': True,
    'options': [
        'Bajo',
        'Moderado',
        'Alto',
        'Crítico'
    ]
}

CAMPO_FRECUENCIA = {
    'name': 'frecuencia_problema',
    'label': '¿Con qué frecuencia ocurre?',
    'type': 'select',
    'required': True,
    'options': [
        'Primera vez',
        'Ocasional',
        'Frecuente',
        'Diario'
    ]
}

CAMPO_AFECTADOS = {
    'name': 'personas_afectadas',
    'label': 'Personas afectadas aproximadamente',
    'type': 'number',
    'required': False,
}

EJES_CIUDADANIA = {
    'salud': {
        'nombre': 'Salud',
        'icono': '🏥',
        'color': '#3182ce',
        'descripcion': 'Atención médica, medicamentos, centros de salud y programas de prevención en el Estado de México.',
        'ubicaciones_titulo': ETIQUETAS_UBICACION['salud'],
        'dependencias': [
            {'clave': 'sedesa', 'nombre': 'SEDESA — Secretaría de Salud', 'rol': 'Coordinación y atención primaria'},
            {'clave': 'imss_bienestar', 'nombre': 'IMSS-Bienestar Edomex', 'rol': 'Afiliación y consulta especializada'},
            {'clave': 'mita', 'nombre': 'Coordinación MITA', 'rol': 'Vinculación interinstitucional'},
        ],
        'campos': CAMPOS_CONTACTO + [
            MUNICIPIO_EDOMEX,
            {'name': 'tipo_enfermedad', 'label': 'Tipo de enfermedad', 'type': 'select', 'required': True,
             'options': TIPOS_ENFERMEDAD},
            {'name': 'medicamentos', 'label': 'Medicamentos que necesita (seleccione todos los que aplican)', 'type': 'checkbox_list', 'required': True,
             'options': MEDICAMENTOS_SALUD},
            {'name': 'centro_salud', 'label': 'Centro de salud (Red ISSEM / SEDESA — Edomex)', 'type': 'centro_salud', 'required': True,
             'depende_municipio': True},
            {'name': 'tipo_atencion', 'label': 'Tipo de atención requerida', 'type': 'select', 'required': True,
             'options': ['Consulta general', 'Medicamentos', 'Especialista', 'Emergencia', 'Programa de prevención']},
            {'name': 'descripcion_problema', 'label': 'Describa su situación de salud', 'type': 'textarea', 'required': True},
            {'name': 'tiene_seguro', 'label': '¿Cuenta con seguridad social?', 'type': 'select', 'required': True,
             'options': ['Sí — IMSS', 'Sí — ISSSTE', 'Sí — IMSS-Bienestar', 'No', 'No sabe']},
            {'name': 'urgencia', 'label': 'Nivel de urgencia', 'type': 'select', 'required': True,
             'options': ['Baja', 'Media', 'Alta', 'Emergencia']},
    CAMPO_IMPACTO_SOCIAL,
    CAMPO_FRECUENCIA,
    CAMPO_AFECTADOS,
        ],
    },

    'educacion': {
        'nombre': 'Educación',
        'icono': '📚',
        'color': '#805ad5',
        'descripcion': 'Infraestructura escolar, acceso, becas, bullying y calidad educativa en el Estado de México.',
        'ubicaciones_titulo': ETIQUETAS_UBICACION['educacion'],
        'dependencias': [
            {'clave': 'sep_edomex', 'nombre': 'SEIEM — Secretaría de Educación', 'rol': 'Atención escolar y becas'},
            {'clave': 'cecyctem', 'nombre': 'CECyTEM', 'rol': 'Educación media superior y técnica'},
            {'clave': 'mita', 'nombre': 'Coordinación MITA', 'rol': 'Seguimiento transversal'},
        ],
        'campos': CAMPOS_CONTACTO + [
            MUNICIPIO_EDOMEX,
            {'name': 'nivel_educativo', 'label': 'Nivel educativo', 'type': 'select', 'required': True,
             'options': ['Preescolar', 'Primaria', 'Secundaria', 'Preparatoria', 'Universidad']},
            {'name': 'institucion', 'label': 'Nombre de la escuela o institución', 'type': 'text', 'required': True},
            {'name': 'tipo_problema', 'label': 'Tipo de problemática', 'type': 'select', 'required': True,
             'options': ['Infraestructura', 'Bullying', 'Falta de acceso', 'Becas', 'Calidad docente', 'Otro']},
            {'name': 'descripcion_problema', 'label': 'Describa la situación', 'type': 'textarea', 'required': True},
            {'name': 'beneficiarios', 'label': '¿Cuántas personas se ven afectadas?', 'type': 'number', 'required': False},
CAMPO_IMPACTO_SOCIAL,
CAMPO_FRECUENCIA,
        ],
    },
    'corrupcion': {
        'nombre': 'Corrupción',
        'icono': '⚖️',
        'color': '#c53030',
        'descripcion': 'Denuncia de actos de corrupción, malversación o abuso de autoridad en el Estado de México.',
        'ubicaciones_titulo': ETIQUETAS_UBICACION['corrupcion'],
        'dependencias': [
            {'clave': 'contraloria', 'nombre': 'Contraloría del Estado de México', 'rol': 'Investigación administrativa'},
            {'clave': 'fgjem', 'nombre': 'Fiscalía General de Justicia Edomex', 'rol': 'Investigación penal'},
            {'clave': 'sev', 'nombre': 'Secretaría de la Honestidad', 'rol': 'Canalización y seguimiento'},
        ],
        'campos': [
            MUNICIPIO_EDOMEX,
            {'name': 'tipo_hecho', 'label': 'Tipo de hecho', 'type': 'select', 'required': True,
             'options': ['Soborno', 'Malversación', 'Abuso de autoridad', 'Nepotismo', 'Tráfico de influencias', 'Otro']},
            {'name': 'dependencia_involucrada', 'label': 'Dependencia o servidor público involucrado', 'type': 'text', 'required': True},
            {'name': 'fecha_hecho', 'label': 'Fecha aproximada del hecho', 'type': 'text', 'required': False},
            {'name': 'descripcion_problema', 'label': 'Describa los hechos con el mayor detalle posible', 'type': 'textarea', 'required': True},
            {'name': 'tiene_evidencia', 'label': '¿Cuenta con evidencia?', 'type': 'select', 'required': True,
             'options': ['Sí — documentos', 'Sí — testigos', 'Sí — ambos', 'No']},
            {'name': 'anonimo', 'label': '¿Desea permanecer en anonimato?', 'type': 'select', 'required': True,
             'options': ['Sí', 'No']},
             CAMPO_IMPACTO_SOCIAL,
CAMPO_FRECUENCIA,
CAMPO_AFECTADOS,
        ],
    },
    'economia': {
        'nombre': 'Economía',
        'icono': '💰',
        'color': '#276749',
        'descripcion': 'Apoyos económicos, programas sociales, finanzas personales y comercio en el Estado de México.',
        'ubicaciones_titulo': ETIQUETAS_UBICACION['economia'],
        'dependencias': [
            {'clave': 'finanzas', 'nombre': 'Secretaría de Finanzas', 'rol': 'Programas fiscales y apoyos'},
            {'clave': 'desarrollo_economico', 'nombre': 'Secretaría de Desarrollo Económico', 'rol': 'Emprendimiento y MIPYMES'},
            {'clave': 'dif', 'nombre': 'DIF Estado de México', 'rol': 'Apoyos sociales'},
        ],
        'campos': [
            MUNICIPIO_EDOMEX,
            {'name': 'tipo_situacion', 'label': 'Tipo de situación', 'type': 'select', 'required': True,
             'options': ['Apoyo económico', 'Crédito', 'Programa social', 'Impuestos', 'Comercio informal', 'Otro']},
            {'name': 'descripcion_problema', 'label': 'Describa su situación económica', 'type': 'textarea', 'required': True},
            {'name': 'sector', 'label': 'Sector o actividad', 'type': 'text', 'required': False},
            {'name': 'apoyo_solicitado', 'label': '¿Qué apoyo solicita?', 'type': 'text', 'required': True},
        CAMPO_IMPACTO_SOCIAL,
CAMPO_FRECUENCIA,
CAMPO_AFECTADOS,
        ],
    },
    'empleo': {
        'nombre': 'Empleo',
        'icono': '💼',
        'color': '#d69e2e',
        'descripcion': 'Búsqueda de empleo, capacitación, ferias de trabajo y derechos laborales en el Estado de México.',
        'ubicaciones_titulo': ETIQUETAS_UBICACION['empleo'],
        'dependencias': [
            {'clave': 'trabajo', 'nombre': 'Secretaría del Trabajo Edomex', 'rol': 'Vinculación laboral y ferias'},
            {'clave': 'stps', 'nombre': 'STPS — Delegación Edomex', 'rol': 'Capacitación y derechos laborales'},
            {'clave': 'cecyctem', 'nombre': 'CECyTEM', 'rol': 'Capacitación técnica'},
        ],
        'campos': CAMPOS_CONTACTO + [
            MUNICIPIO_EDOMEX,
            {'name': 'edad', 'label': 'Edad', 'type': 'number', 'required': True, 'min': 18, 'max': 100},
            {'name': 'tipo_solicitud', 'label': 'Tipo de solicitud', 'type': 'select', 'required': True,
             'options': ['Busco empleo', 'Capacitación', 'Denuncia laboral', 'Feria de empleo', 'Otro']},
            {'name': 'escolaridad', 'label': 'Escolaridad', 'type': 'select', 'required': True,
             'options': ['Primaria', 'Secundaria', 'Preparatoria', 'Técnico', 'Licenciatura', 'Posgrado']},
            {'name': 'experiencia', 'label': 'Años de experiencia (deje vacío si no tiene)', 'type': 'number', 'required': False},
            {'name': 'tipo_trabajo_buscado', 'label': 'Tipo de trabajo que busca', 'type': 'select', 'required': False,
             'condicion_edad_min': 50,
             'options': ['Tiempo completo', 'Medio tiempo', 'Trabajo desde casa', 'Empleo temporal', 'Reconversión profesional', 'No estoy seguro']},
            {'name': 'descripcion_problema', 'label': 'Describa su situación laboral', 'type': 'textarea', 'required': True},
       CAMPO_IMPACTO_SOCIAL,
CAMPO_FRECUENCIA,
CAMPO_AFECTADOS,
        ],
    },
    'seguridad': {
        'nombre': 'Seguridad',
        'icono': '🛡️',
        'color': '#2c5282',
        'descripcion': 'Denuncias de inseguridad, violencia, robos y solicitud de patrullaje en el Estado de México.',
        'ubicaciones_titulo': ETIQUETAS_UBICACION['seguridad'],
        'dependencias': [
            {'clave': 'seguridad', 'nombre': 'Secretaría de Seguridad Edomex', 'rol': 'Patrullaje y prevención'},
            {'clave': 'fgjem', 'nombre': 'Fiscalía General de Justicia Edomex', 'rol': 'Investigación ministerial'},
            {'clave': '911', 'nombre': 'C5 Edomex — Centro de Emergencias', 'rol': 'Emergencias inmediatas'},
        ],
        'campos': CAMPOS_CONTACTO + [
            MUNICIPIO_EDOMEX,
            {'name': 'tipo_incidente', 'label': 'Tipo de incidente', 'type': 'select', 'required': True,
             'options': ['Robo', 'Violencia familiar', 'Vandalismo', 'Extorsión', 'Desaparición', 'Otro']},
            {'name': 'fecha_incidente', 'label': 'Fecha del incidente', 'type': 'text', 'required': False},
            {'name': 'zona', 'label': 'Colonia o zona', 'type': 'text', 'required': True},
            {'name': 'descripcion_problema', 'label': 'Describa lo ocurrido', 'type': 'textarea', 'required': True},
            {'name': 'denuncia_previa', 'label': '¿Presentó denuncia anterior?', 'type': 'select', 'required': True,
             'options': ['Sí — Fiscalía', 'Sí — Ministerio Público en línea', 'No']},
         CAMPO_IMPACTO_SOCIAL,
CAMPO_FRECUENCIA,
CAMPO_AFECTADOS,
        ],
    },
'agua': {
    'nombre': 'Agua',
    'icono': '💧',
    'color': '#0891b2',

    'etiquetas_busqueda': [
        'desabasto',
        'fuga',
        'agua contaminada',
        'presión baja',
        'drenaje',
        'inundación',
        'infraestructura hidráulica',
        'organismo operador',
        'CAEM'
    ],

    'descripcion': 'Desabasto, fugas, contaminación, presión baja y problemas de infraestructura hídrica.',
    'ubicaciones_titulo': ETIQUETAS_UBICACION['agua'],

    'dependencias': [
        {
            'clave': 'caem',
            'nombre': 'CAEM — Comisión del Agua del Estado de México',
            'rol': 'Coordinación hídrica estatal'
        },
        {
            'clave': 'organismo_agua',
            'nombre': 'Organismo operador municipal de agua',
            'rol': 'Atención local'
        },
        {
            'clave': 'mita',
            'nombre': 'Coordinación MITA',
            'rol': 'Análisis territorial y prevención'
        },
    ],

    'campos': CAMPOS_CONTACTO + [
        MUNICIPIO_EDOMEX,

        {
            'name': 'colonia',
            'label': 'Colonia o comunidad',
            'type': 'text',
            'required': True
        },

        {
            'name': 'tipo_problema_agua',
            'label': 'Tipo de problemática',
            'type': 'select',
            'required': True,
            'options': [
                'Desabasto',
                'Fuga',
                'Agua contaminada',
                'Presión baja',
                'Drenaje',
                'Inundación',
                'Otro'
            ]
        },

        {
            'name': 'frecuencia',
            'label': 'Frecuencia',
            'type': 'select',
            'required': True,
            'options': [
                'Una vez',
                'Ocasional',
                'Frecuente',
                'Permanente'
            ]
        },

        {
            'name': 'personas_afectadas',
            'label': 'Personas afectadas aproximadamente',
            'type': 'number',
            'required': False
        },

        {
            'name': 'descripcion_problema',
            'label': 'Describa la problemática del agua',
            'type': 'textarea',
            'required': True
        },

        {
            'name': 'evidencia',
            'label': '¿Cuenta con evidencia?',
            'type': 'select',
            'required': True,
            'options': [
                'Sí — foto/video',
                'Sí — documento',
                'Sí — testigos',
                'No'
            ]
        },

        {
            'name': 'urgencia',
            'label': 'Nivel de urgencia',
            'type': 'select',
            'required': True,
            'options': [
                'Baja',
                'Media',
                'Alta',
                'Crítica'
            ]
        },

        CAMPO_IMPACTO_SOCIAL,
    ],
},
}




def get_eje_config(eje_slug):
    return EJES_CIUDADANIA.get(eje_slug, {})


def listar_ejes():
    return [
        {'slug': slug, **cfg}
        for slug, cfg in EJES_CIUDADANIA.items()
    ]


def etiqueta_ubicaciones(eje_slug):
    return ETIQUETAS_UBICACION.get(eje_slug, f'Puntos de atención en {ENTIDAD}')
