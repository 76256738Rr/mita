"""Servicios para reportes ciudadanos y asistente IA simulado."""

import uuid
from datetime import date, datetime, timedelta

from django.utils import timezone

from core.ciudadania_config import EJES_CIUDADANIA, get_eje_config
from core.models import MensajeReporteCiudadano, ReporteCiudadano


PERSONAS_ATENCION = {
    'mita': {
        'nombre': 'Lic. Patricia Morales',
        'cargo': 'Gestora de ventanilla ciudadana',
        'correo': 'ventanilla@mita.edomex.gob.mx',
    },
    'sedesa': {
        'nombre': 'Lic. María Elena Santos',
        'cargo': 'Enlace ciudadano — surtimiento de medicamentos',
        'correo': 'enlace.ciudadano@sedesa.edomex.gob.mx',
    },
    'imss_bienestar': {
        'nombre': 'Dr. Jorge Ramírez López',
        'cargo': 'Coordinador de afiliación IMSS-Bienestar',
        'correo': 'jorge.ramirez@imssbienestar.gob.mx',
    },
    'sep_edomex': {
        'nombre': 'Prof. Carmen Delgado',
        'cargo': 'Enlace escolar — SEIEM',
        'correo': 'carmen.delgado@seiem.edomex.gob.mx',
    },
    'cecyctem': {
        'nombre': 'Ing. Luis Hernández',
        'cargo': 'Orientador educativo CECyTEM',
        'correo': 'l.hernandez@cecytem.edomex.gob.mx',
    },
    'stps': {
        'nombre': 'Lic. Ana Ruiz García',
        'cargo': 'Asesora de empleo — Secretaría del Trabajo',
        'correo': 'ana.ruiz@trabajo.edomex.gob.mx',
    },
    'fiscalia': {
        'nombre': 'Lic. Roberto Méndez',
        'cargo': 'Enlace de denuncia ciudadana',
        'correo': 'roberto.mendez@fiscalia.edomex.gob.mx',
    },
    'contraloria': {
        'nombre': 'Lic. Sandra Ortiz',
        'cargo': 'Investigadora de denuncias anticorrupción',
        'correo': 'sandra.ortiz@contraloria.edomex.gob.mx',
    },
    'economia': {
        'nombre': 'C.P. Miguel Torres',
        'cargo': 'Enlace de apoyo económico',
        'correo': 'm.torres@economia.edomex.gob.mx',
    },
    'seguridad': {
        'nombre': 'Cmdte. Javier Núñez',
        'cargo': 'Coordinador de atención ciudadana — SSP',
        'correo': 'j.nunez@seguridad.edomex.gob.mx',
    },
}


def _iso(dt):
    if not dt:
        return None
    if isinstance(dt, str):
        return dt
    return dt.isoformat()


def _fmt_fecha(iso_val):
    if not iso_val:
        return '—'
    try:
        dt = datetime.fromisoformat(iso_val.replace('Z', '+00:00'))
        if timezone.is_aware(dt):
            dt = timezone.localtime(dt)
        return dt.strftime('%d/%m/%Y %H:%M')
    except (ValueError, TypeError):
        return iso_val


def persona_para_dependencia(dep):
    clave = dep.get('clave', 'mita')
    base = PERSONAS_ATENCION.get(clave, PERSONAS_ATENCION['mita']).copy()
    base['dependencia'] = dep['nombre']
    base['clave'] = clave
    return base


def construir_ruta_tramite(eje_slug, dependencias, fecha_base=None):
    """Ruta de atención con dependencias, responsables y marcas de tiempo."""
    eje = get_eje_config(eje_slug)
    base = fecha_base or timezone.now()
    pasos = []

    def add_paso(orden, nombre, dependencia, clave, estado, descripcion, delta_recibido, delta_inicio=None, delta_fin=None):
        recibido = base + timedelta(minutes=delta_recibido)
        inicio = base + timedelta(minutes=delta_inicio) if delta_inicio is not None else None
        fin = base + timedelta(minutes=delta_fin) if delta_fin is not None else None
        persona = persona_para_dependencia({'clave': clave, 'nombre': dependencia})
        pasos.append({
            'orden': orden,
            'nombre': nombre,
            'dependencia': dependencia,
            'clave': clave,
            'estado': estado,
            'descripcion': descripcion,
            'responsable': persona,
            'fecha_recibido': _iso(recibido),
            'fecha_inicio_atencion': _iso(inicio) if estado != 'pendiente' else None,
            'fecha_fin': _iso(fin) if estado == 'completado' else None,
            'fecha_recibido_fmt': _fmt_fecha(_iso(recibido)),
            'fecha_inicio_atencion_fmt': _fmt_fecha(_iso(inicio)) if inicio else '—',
            'fecha_fin_fmt': _fmt_fecha(_iso(fin)) if fin else '—',
        })

    add_paso(
        1, 'Recepción en ventanilla', 'Ventanilla Ciudadana MITA', 'mita', 'completado',
        'Su reporte fue recibido, validado y registrado con número de control.',
        0, 5, 15,
    )
    add_paso(
        2, 'Clasificación por eje', f"Coordinación Eje {eje.get('nombre', eje_slug)}", 'mita', 'completado',
        'El sistema clasificó su problemática y determinó las dependencias competentes.',
        15, 20, 30,
    )

    for i, dep in enumerate(dependencias):
        orden = i + 3
        es_primera = i == 0
        estado = 'activo' if es_primera else 'pendiente'
        delta_rec = 30 + (i * 60)
        delta_ini = delta_rec + 30 if es_primera else None
        add_paso(
            orden,
            'Atención directa' if es_primera else 'Coordinación interinstitucional',
            dep['nombre'],
            dep.get('clave', 'mita'),
            estado,
            dep.get('rol', 'Atención institucional al ciudadano'),
            delta_rec,
            delta_ini,
            delta_rec + 45 if estado == 'completado' else None,
        )

    pasos.append({
        'orden': len(pasos) + 1,
        'nombre': 'Respuesta oficial al ciudadano',
        'dependencia': dependencias[0]['nombre'] if dependencias else 'Coordinación MITA',
        'clave': dependencias[0].get('clave', 'mita') if dependencias else 'mita',
        'estado': 'pendiente',
        'descripcion': 'Se emitirá resolución, acción concreta o informe de no procedencia.',
        'responsable': persona_para_dependencia(dependencias[0] if dependencias else {'clave': 'mita', 'nombre': 'Coordinación MITA'}),
        'fecha_recibido': None,
        'fecha_inicio_atencion': None,
        'fecha_fin': None,
        'fecha_recibido_fmt': '—',
        'fecha_inicio_atencion_fmt': '—',
        'fecha_fin_fmt': '—',
    })
    return pasos


def obtener_responsable_activo(ruta_tramite):
    for paso in ruta_tramite or []:
        if paso.get('estado') == 'activo':
            return paso.get('responsable', {})
    return {}


def marcar_inicio_atencion(reporte):
    """Registra cuándo la dependencia activa empezó a atender el caso."""
    ruta = list(reporte.ruta_tramite or [])
    ahora = timezone.now()
    cambio = False
    for paso in ruta:
        if paso.get('estado') == 'activo' and not paso.get('fecha_inicio_atencion'):
            paso['fecha_inicio_atencion'] = _iso(ahora)
            paso['fecha_inicio_atencion_fmt'] = _fmt_fecha(_iso(ahora))
            reporte.responsable_atencion = paso.get('responsable', {})
            cambio = True
            break
    if cambio:
        reporte.ruta_tramite = ruta
        reporte.save(update_fields=['ruta_tramite', 'responsable_atencion', 'actualizado_en'])
    return reporte


def enriquecer_ruta_demo(reporte, dias_atras=3):
    """Ajusta fechas de la ruta demo para simular seguimiento en curso."""
    base = timezone.now() - timedelta(days=dias_atras)
    deps = reporte.dependencias_involucradas or get_eje_config(reporte.eje).get('dependencias', [])
    ruta = construir_ruta_tramite(reporte.eje, deps, fecha_base=base)
    reporte.ruta_tramite = ruta
    reporte.responsable_atencion = obtener_responsable_activo(ruta)
    reporte.estado = ReporteCiudadano.Estado.EN_ATENCION
    reporte.save(update_fields=['ruta_tramite', 'responsable_atencion', 'estado', 'actualizado_en'])
    return reporte


WORKFLOW_ICONOS = {
    'recepcion': 'img/ciudadania/workflow/paso-recepcion.svg',
    'clasificacion': 'img/ciudadania/workflow/paso-clasificacion.svg',
    'atencion': 'img/ciudadania/workflow/paso-atencion.svg',
    'coordinacion': 'img/ciudadania/workflow/paso-coordinacion.svg',
    'respuesta': 'img/ciudadania/workflow/paso-respuesta.svg',
}


def tipo_icono_paso(paso):
    """Determina el ícono gráfico según el tipo de paso en la ruta."""
    nombre = (paso.get('nombre') or '').lower()
    if 'recepción' in nombre or 'recepcion' in nombre:
        return 'recepcion'
    if 'clasificación' in nombre or 'clasificacion' in nombre:
        return 'clasificacion'
    if 'respuesta' in nombre:
        return 'respuesta'
    if 'coordinación' in nombre or 'coordinacion' in nombre:
        return 'coordinacion'
    if 'atención' in nombre or 'atencion' in nombre or 'turnado' in nombre:
        return 'atencion'
    return 'atencion'


def enriquecer_ruta_grafica(ruta_tramite):
    """Añade metadatos visuales a cada paso para la vista gráfica."""
    resultado = []
    for paso in ruta_tramite or []:
        copia = dict(paso)
        tipo = tipo_icono_paso(paso)
        copia['icono_tipo'] = tipo
        copia['icono'] = WORKFLOW_ICONOS.get(tipo, WORKFLOW_ICONOS['atencion'])
        copia['estado_label'] = {
            'completado': 'Completado',
            'activo': 'En atención',
            'pendiente': 'Pendiente',
        }.get(paso.get('estado'), paso.get('estado', ''))
        resultado.append(copia)
    return resultado


def generar_numero_control():
    """Genera folio único MITA-CIU-YYYY-NNNNN."""
    year = timezone.now().year
    prefix = f'MITA-CIU-{year}-'
    ultimo = (
        ReporteCiudadano.objects.filter(numero_control__startswith=prefix)
        .order_by('-numero_control')
        .first()
    )
    if ultimo:
        try:
            seq = int(ultimo.numero_control.split('-')[-1]) + 1
        except ValueError:
            seq = 1
    else:
        seq = 1
    return f'{prefix}{seq:05d}'


def estimar_fecha_atencion(eje_slug, urgencia=None):
    """Estima fecha de atención según eje y urgencia."""
    dias = {
        'salud': 5 if urgencia in ('Alta', 'Emergencia') else 15,
        'educacion': 20,
        'corrupcion': 30,
        'economia': 25,
        'empleo': 15,
        'seguridad': 3 if urgencia else 10,
    }
    base = dias.get(eje_slug, 20)
    return date.today() + timedelta(days=base)


def registrar_mensaje(reporte=None, sesion_key='', tipo_autor='ia', autor_nombre='Asistente IA MITA',
                      contenido='', metadata=None):
    return MensajeReporteCiudadano.objects.create(
        reporte=reporte,
        sesion_key=sesion_key,
        tipo_autor=tipo_autor,
        autor_nombre=autor_nombre,
        contenido=contenido,
        metadata=metadata or {},
    )


def _entero(val, default=None):
    if val is None or val == '':
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def analizar_perfil_empleo(datos):
    """Perfil laboral para recomendaciones IA (eje empleo)."""
    datos = datos or {}
    edad = _entero(datos.get('edad'), 0)
    experiencia = _entero(datos.get('experiencia'), None)
    escolaridad = datos.get('escolaridad', '')
    tipo_trabajo = datos.get('tipo_trabajo_buscado', '')
    municipio = datos.get('municipio', 'su municipio')

    sin_experiencia = experiencia is None or experiencia == 0
    mucha_experiencia = experiencia is not None and experiencia >= 10
    adulto_mayor = edad > 50

    recomendaciones = []
    if adulto_mayor and sin_experiencia:
        recomendaciones = [
            'Programa de Empleo para Adultos Mayores — Edomex',
            'Capacitación técnica express en CECyTEM (6 a 12 semanas)',
            'Ferias de empleo con empresas inclusivas (+50)',
            'Roles de apoyo comunitario, orientación escolar o cuidado de personas',
            'Empleo temporal en programas estatales de servicio social',
        ]
    elif adulto_mayor and not sin_experiencia:
        recomendaciones = [
            'Bolsa de empleo especializada STPS — perfil senior',
            'Vinculación con empresas que valoran experiencia (+50)',
            'Asesoría o mentoría en su área de expertise',
            'Medio tiempo o trabajo híbrido según su preferencia',
            'Feria de empleo sectorial en ' + (municipio or 'su región'),
        ]
    elif mucha_experiencia:
        recomendaciones = [
            'Bolsa de Empleo Especializada — Secretaría del Trabajo Edomex',
            'Vinculación directa con empresas del sector (prioridad por experiencia)',
            'Roles de supervisión, coordinación o consultoría',
            'Feria ejecutiva de empleo y networking empresarial',
            'Programa de reconversión si desea cambiar de sector',
        ]
    elif sin_experiencia:
        recomendaciones = [
            'Programa Primer Empleo Edomex',
            'Capacitación para el trabajo — STPS (beca + certificación)',
            'Ferias de empleo para jóvenes y primer ingreso',
            'Prácticas y becas en CECyTEM según su escolaridad',
            'Orientación vocacional gratuita en módulos del trabajador',
        ]
    else:
        recomendaciones = [
            'Feria de empleo municipal en ' + (municipio or 'su región'),
            'Bolsa estatal de trabajo según su perfil (' + str(experiencia) + ' años de experiencia)',
            'Capacitación complementaria para mejorar su empleabilidad',
        ]

    return {
        'edad': edad,
        'experiencia': experiencia,
        'sin_experiencia': sin_experiencia,
        'mucha_experiencia': mucha_experiencia,
        'adulto_mayor': adulto_mayor,
        'escolaridad': escolaridad,
        'tipo_trabajo_buscado': tipo_trabajo,
        'recomendaciones': recomendaciones,
    }


def respuesta_empleo_ia(mensaje, datos_parciales=None, fase='exploracion'):
    """Respuestas IA especializadas para el eje empleo."""
    datos = datos_parciales or {}
    perfil = analizar_perfil_empleo(datos)
    msg = (mensaje or '').lower().strip()
    recs = '\n'.join(f'• {r}' for r in perfil['recomendaciones'])

    if fase == 'bienvenida_eje':
        return (
            'Ha seleccionado el eje **Empleo**. Complete sus datos de contacto, **edad**, escolaridad y experiencia.\n\n'
            '**Importante:** si tiene **más de 50 años**, le preguntaré qué tipo de trabajo busca y podré recomendarle '
            'opciones acordes a su perfil. Si no tiene experiencia o si cuenta con **mucha experiencia**, '
            'ajustaré las oportunidades laborales sugeridas.\n\n'
            'Dependencias: Secretaría del Trabajo Edomex, STPS y CECyTEM.'
        )

    if fase == 'analisis_empleo':
        if perfil['edad'] <= 0:
            return 'Indique su **edad** en el formulario para personalizar recomendaciones de empleo.'

        if perfil['adulto_mayor']:
            intro = (
                f'Veo que tiene **{perfil["edad"]} años**. '
                '¿Qué tipo de trabajo busca? Puede indicarlo en el campo del formulario o escribirme aquí '
                '(tiempo completo, medio tiempo, desde casa, temporal, etc.).\n\n'
            )
        else:
            intro = f'Perfil registrado: **{perfil["edad"]} años**. '

        if perfil['sin_experiencia']:
            exp_txt = (
                'Registré que **no tiene experiencia laboral** o es su primer empleo. '
                'Le orientaré hacia programas de capacitación e inserción inicial:\n\n'
            )
        elif perfil['mucha_experiencia']:
            exp_txt = (
                f'Con **{perfil["experiencia"]} años de experiencia**, puede acceder a mejores oportunidades '
                'y vinculación preferente con empresas:\n\n'
            )
        else:
            exp_txt = (
                f'Con **{perfil["experiencia"]} años de experiencia**, estas opciones se ajustan a su perfil:\n\n'
            )

        tipo = perfil.get('tipo_trabajo_buscado')
        tipo_txt = ''
        if tipo:
            tipo_txt = f'\n\nTipo de trabajo indicado: **{tipo}**. Ajustaremos su turnado a ferias y vacantes compatibles.'

        return intro + exp_txt + recs + tipo_txt

    if perfil['adulto_mayor'] and any(w in msg for w in (
        'trabajo', 'empleo', 'busco', 'recomi', 'opcion', 'opción', 'tipo', 'puesto', 'oficio'
    )):
        pregunta = (
            f'Con **{perfil["edad"]} años**, ¿qué tipo de trabajo busca? '
            'Por ejemplo: tiempo completo, medio tiempo, desde casa, empleo temporal o reconversión profesional.\n\n'
        )
        if perfil['sin_experiencia']:
            pregunta += (
                'Al no registrar experiencia previa, le sugiero iniciar con capacitación y ferias inclusivas:\n\n'
            )
        elif perfil['mucha_experiencia']:
            pregunta += (
                'Su experiencia le permite acceder a vacantes de mayor responsabilidad:\n\n'
            )
        return pregunta + recs

    if any(w in msg for w in ('recomi', 'suger', 'oportunidad', 'vacante', 'feria', 'capacit')):
        if perfil['edad'] <= 0:
            return 'Indique su edad y años de experiencia en el formulario para recomendarle oportunidades adecuadas.'
        header = 'Según su perfil, estas son las **mejores oportunidades** identificadas:\n\n'
        if perfil['mucha_experiencia']:
            header = 'Por su **amplia experiencia**, estas opciones ofrecen mejor vinculación:\n\n'
        elif perfil['sin_experiencia']:
            header = 'Sin experiencia registrada, le recomendamos iniciar por estos programas:\n\n'
        return header + recs

    if any(w in msg for w in ('experiencia', 'años', 'anos', 'nunca he trabajado', 'sin experiencia')):
        if perfil['sin_experiencia']:
            return (
                'Si **no tiene experiencia laboral**, no se preocupe: existen programas de primer empleo, '
                'becas de capacitación STPS y ferias orientadas a quienes inician su trayectoria:\n\n' + recs
            )
        if perfil['mucha_experiencia']:
            return (
                f'Con **{perfil["experiencia"]} años de experiencia** califica para bolsa especializada, '
                'roles de coordinación y vinculación directa con empresas:\n\n' + recs
            )
        return (
            f'Con **{perfil["experiencia"]} años de experiencia** estas opciones son adecuadas:\n\n' + recs
        )

    if perfil['edad'] > 0:
        return respuesta_empleo_ia('', datos, fase='analisis_empleo')

    return None


def respuesta_asistente_ia(mensaje, eje_slug=None, datos_parciales=None, fase='exploracion'):
    """Simula respuestas del asistente IA según contexto."""
    if eje_slug == 'empleo':
        empleo_resp = respuesta_empleo_ia(mensaje, datos_parciales, fase)
        if empleo_resp:
            return empleo_resp

    if eje_slug == 'salud':
        if fase == 'bienvenida_eje':
            return (
                'Ha seleccionado el eje **Salud** en el **Estado de México**. '
                'Indique su municipio, **tipo de enfermedad** y los **medicamentos** que necesita. '
                'El mapa muestra centros de salud y farmacias estatales cercanas a su municipio.'
            )
        msg_l = (mensaje or '').lower()
        if any(w in msg_l for w in ('medicamento', 'enfermedad', 'centro', 'mapa', 'ubicación', 'ubicacion', 'farmacia')):
            mun = (datos_parciales or {}).get('municipio', 'su municipio')
            meds = (datos_parciales or {}).get('medicamentos', [])
            if isinstance(meds, list) and meds:
                med_txt = ', '.join(meds[:5])
                return (
                    f'Para **{mun}**, Edomex, revise el mapa de centros de salud. '
                    f'Medicamentos solicitados: {med_txt}. '
                    'Puede acudir al centro más cercano o registrar su reporte para surtimiento SEDESA.'
                )
            return (
                f'Seleccione su **municipio** en el formulario para ver centros de salud en el mapa de Edomex. '
                'Marque los medicamentos que necesita en la lista del formulario.'
            )

    msg = (mensaje or '').lower().strip()
    eje_cfg = get_eje_config(eje_slug) if eje_slug else {}
    eje_nombre = eje_cfg.get('nombre', 'su eje')

    if not eje_slug:
        return (
            '¡Hola! Soy el Asistente IA de la Ventanilla Ciudadana MITA. '
            'Primero seleccione un eje (Salud, Educación, Corrupción, Economía, Empleo o Seguridad). '
            'Le mostraré los campos necesarios y las dependencias que atenderán su caso.'
        )

    if fase == 'bienvenida_eje' and eje_slug not in ('salud', 'empleo'):
        deps = eje_cfg.get('dependencias', [])
        dep_text = '\n'.join(f"• **{d['nombre']}** — {d['rol']}" for d in deps)
        campos = eje_cfg.get('campos', [])
        req = [c['label'] for c in campos if c.get('required')]
        return (
            f"Ha seleccionado el eje **{eje_nombre}**. {eje_cfg.get('descripcion', '')}\n\n"
            f"**Dependencias que podrían intervenir:**\n{dep_text}\n\n"
            f"Complete los campos del formulario. Datos obligatorios: {', '.join(req[:4])}..."
            "\n\nConsulte el **mapa de ubicaciones en Edomex** según su municipio."
            "\n\nPuede preguntarme cómo llenar algún campo o pedirme que revise su descripción antes de enviar."
        )

    if any(w in msg for w in ('dependencia', 'dependencias', 'quien atiende', 'quién atiende', 'turnado')):
        deps = eje_cfg.get('dependencias', [])
        lines = [f"• {d['nombre']}: {d['rol']}" for d in deps]
        return (
            f"Para el eje **{eje_nombre}**, las dependencias involucradas serían:\n"
            + '\n'.join(lines)
            + '\n\nAl enviar su reporte recibirá un **número de control** y la **ruta de turnado** oficial.'
        )

    if any(w in msg for w in ('numero', 'número', 'control', 'folio')):
        return (
            'Al registrar su problemática el sistema generará un número de control con formato '
            '**MITA-CIU-2026-XXXXX**. Guárdelo para dar seguimiento y chatear con la dependencia turnada.'
        )

    if any(w in msg for w in ('ayuda', 'help', 'como lleno', 'cómo lleno', 'ejemplo')):
        return (
            f'Para el eje {eje_nombre}, describa su situación con hechos concretos: '
            '¿qué ocurrió?, ¿dónde?, ¿cuándo? y ¿qué apoyo necesita? '
            'Entre más clara sea su descripción, más rápido podrá turnarse a la dependencia correcta.'
        )

    if any(w in msg for w in ('revisar', 'revisa', 'está bien', 'esta bien', 'correcto')) and datos_parciales:
        desc = datos_parciales.get('descripcion_problema', '')
        if len(desc) < 30:
            return (
                'Su descripción es muy breve. Agregue más detalle: lugar, fecha aproximada, '
                'personas afectadas y qué resultado espera. Esto ayuda a la dependencia a resolver su caso.'
            )
        return (
            'Su descripción se ve adecuada. Revise que el municipio y los datos de contacto sean correctos. '
            'Cuando esté listo, pulse **Registrar mi problemática** para obtener su número de control.'
        )

    if datos_parciales and datos_parciales.get('descripcion_problema'):
        return (
            f'Entiendo su situación en el eje {eje_nombre}. '
            'Si necesita ajustar algo, edite el formulario. '
            'También puede preguntarme por las dependencias o pedirme que revise su texto.'
        )

    return (
        f'Estoy aquí para ayudarle con su reporte en el eje **{eje_nombre}**. '
        'Puede preguntar: "¿qué dependencias intervienen?", "¿cómo obtengo mi número de control?" '
        'o "revisa mi descripción".'
    )


def respuesta_responsable_simulada(reporte, mensaje_ciudadano):
    """Simula respuesta del responsable de atención al ciudadano."""
    resp = reporte.responsable_atencion or reporte.responsable_actual or {}
    nombre = resp.get('nombre', 'Enlace ciudadano')
    cargo = resp.get('cargo', '')
    dep = resp.get('dependencia', reporte.dependencia_principal)
    fecha = reporte.fecha_estimada_atencion
    fecha_txt = fecha.strftime('%d/%m/%Y') if fecha else 'próximos días'
    paso = reporte.paso_activo or {}
    inicio = paso.get('fecha_inicio_atencion_fmt', '—')
    recibido = paso.get('fecha_recibido_fmt', '—')
    msg = mensaje_ciudadano.lower()

    if reporte.estado == ReporteCiudadano.Estado.NO_PROCEDE:
        return (
            f'Buen día, soy **{nombre}**, {cargo}.\n\n'
            f'Su reporte **{reporte.numero_control}** no procede. '
            f'Motivo: {reporte.motivo_no_procede or "No cumple requisitos normativos."} '
            'Puede aportar más documentación o solicitar revisión de su caso.'
        )

    if any(w in msg for w in ('quien eres', 'quién eres', 'con quien', 'con quién', 'responsable', 'nombre')):
        return (
            f'Soy **{nombre}**, {cargo} de **{dep}**. '
            f'Fui asignado(a) a su reporte **{reporte.numero_control}**. '
            f'Lo recibimos el **{recibido}** y desde el **{inicio}** estoy dando seguimiento personal.'
        )

    if any(w in msg for w in ('cuando', 'cuándo', 'fecha', 'plazo', 'tiempo', 'recib', 'empez')):
        return (
            f'**{nombre}:** Su caso **{reporte.numero_control}** fue recibido el **{recibido}**. '
            f'Inicié la atención el **{inicio}**. '
            f'La fecha estimada de resolución es **{fecha_txt}**. Le mantendré informado por este chat.'
        )

    if any(w in msg for w in ('como', 'cómo', 'resolver', 'atender', 'proceso', 'paso', 'ruta')):
        return (
            f'**{nombre}:** El proceso incluye revisión de su reporte, verificación con las instancias competentes '
            f'y gestión de la solución solicitada. '
            f'Actualmente su trámite está en **{reporte.get_estado_display()}** dentro de **{dep}**. '
            f'Estimamos concluir antes del **{fecha_txt}**.'
        )

    if any(w in msg for w in ('por que no', 'porqué no', 'no procede', 'rechaz')):
        return (
            f'**{nombre}:** Si no es posible resolver su solicitud, le informaré el fundamento '
            'con claridad. Puede pedir aclaración aquí o escalar a Contraloría si lo considera necesario.'
        )

    if any(w in msg for w in ('gracias', 'ok', 'entendido', 'bien')):
        return (
            f'**{nombre}:** Gracias por su seguimiento. Continúo gestionando su reporte '
            f'**{reporte.numero_control}**. Próxima actualización estimada: **{fecha_txt}**.'
        )

    return (
        f'**{nombre}** ({cargo}):\n'
        f'He recibido su mensaje sobre **{reporte.numero_control}**. '
        f'Su solicitud está en **{reporte.get_estado_display()}**. '
        f'Recibido: **{recibido}** · Atención desde: **{inicio}** · '
        f'Respuesta estimada: **{fecha_txt}**.\n\n'
        '¿Desea saber en qué paso va, quién lo atiende o cuándo habrá resolución?'
    )


def respuesta_dependencia_simulada(reporte, mensaje_ciudadano):
    """Compatibilidad: delega al responsable de atención."""
    return respuesta_responsable_simulada(reporte, mensaje_ciudadano)


def crear_reporte_ciudadano(usuario, eje_slug, titulo, descripcion, datos_captura, municipio='', numero_control=None):
    """Crea reporte con número de control, dependencias y ruta."""
    eje_cfg = get_eje_config(eje_slug)
    dependencias = eje_cfg.get('dependencias', [])
    urgencia = datos_captura.get('urgencia', '')
    numero = numero_control or generar_numero_control()
    fecha_est = estimar_fecha_atencion(eje_slug, urgencia)
    ruta = construir_ruta_tramite(eje_slug, dependencias)
    responsable = obtener_responsable_activo(ruta)

    if eje_slug == 'empleo':
        perfil = analizar_perfil_empleo(datos_captura)
        datos_captura = {**datos_captura, 'recomendaciones_ia': perfil['recomendaciones']}

    reporte = ReporteCiudadano.objects.create(
        numero_control=numero,
        eje=eje_slug,
        titulo=titulo,
        descripcion=descripcion,
        datos_captura=datos_captura,
        municipio=municipio or datos_captura.get('municipio', ''),
        dependencia_principal=dependencias[0]['nombre'] if dependencias else 'Coordinación MITA',
        dependencias_involucradas=dependencias,
        ruta_tramite=ruta,
        responsable_atencion=responsable,
        estado=ReporteCiudadano.Estado.TURNADO,
        fecha_estimada_atencion=fecha_est,
        respuesta_dependencia=(
            f'Su reporte fue turnado a {dependencias[0]["nombre"]}. '
            f'Responsable: {responsable.get("nombre", "Enlace ciudadano")}. '
            f'Fecha estimada de atención: {fecha_est.strftime("%d/%m/%Y")}.'
        ),
        creado_por=usuario,
    )

    paso_activo = reporte.paso_activo or {}
    registrar_mensaje(
        reporte=reporte,
        tipo_autor=MensajeReporteCiudadano.TipoAutor.SISTEMA,
        autor_nombre='Sistema MITA',
        contenido=(
            f'Reporte registrado con número de control **{numero}**. '
            f'Turnado a **{reporte.dependencia_principal}**.'
        ),
    )
    registrar_mensaje(
        reporte=reporte,
        tipo_autor=MensajeReporteCiudadano.TipoAutor.IA,
        autor_nombre='Asistente IA MITA',
        contenido=(
            f'¡Registro exitoso! Su número de control es **{numero}**. '
            f'Siga la **ruta de atención** para ver qué dependencia lo recibió, quién lo atiende y en qué fechas. '
            f'Puede chatear directamente con **{responsable.get("nombre", "su enlace ciudadano")}**.'
            + (
                '\n\n**Oportunidades sugeridas para su perfil:**\n'
                + '\n'.join(f'• {r}' for r in datos_captura.get('recomendaciones_ia', []))
                if eje_slug == 'empleo' and datos_captura.get('recomendaciones_ia') else ''
            )
        ),
        metadata={'dependencias': [d['nombre'] for d in dependencias]},
    )
    registrar_mensaje(
        reporte=reporte,
        tipo_autor=MensajeReporteCiudadano.TipoAutor.RESPONSABLE,
        autor_nombre=responsable.get('nombre', reporte.dependencia_principal),
        contenido=(
            f'Buen día, soy **{responsable.get("nombre", "Enlace ciudadano")}**, '
            f'{responsable.get("cargo", "responsable de atención")}.\n\n'
            f'Recibí su reporte **{numero}** el **{paso_activo.get("fecha_recibido_fmt", "hoy")}**. '
            f'Estoy dando seguimiento personal a su caso. '
            f'Fecha estimada de resolución: **{fecha_est.strftime("%d/%m/%Y")}**.\n\n'
            'Escríbame aquí si tiene dudas sobre plazos, documentos o el avance de su trámite.'
        ),
        metadata={'responsable': responsable},
    )
    return reporte


def nueva_sesion_asistente():
    return str(uuid.uuid4())


def mensaje_bienvenida_general():
    return respuesta_asistente_ia('', eje_slug=None)
