"""Vistas del portal ciudadano — público general."""

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from core.ciudadania_config import EJES_CIUDADANIA, ENTIDAD, get_eje_config, listar_ejes
from core.ciudadania_ubicaciones import obtener_centros_salud, obtener_ubicaciones_eje, ubicaciones_json
from core.ciudadania_services import (
    crear_reporte_ciudadano,
    mensaje_bienvenida_general,
    nueva_sesion_asistente,
    registrar_mensaje,
    respuesta_asistente_ia,
    respuesta_dependencia_simulada,
)
from core.models import MensajeReporteCiudadano, ReporteCiudadano
from core.permissions import es_publico_general, obtener_rol, requiere_publico


def _titulo_desde_datos(eje_slug, datos):
    eje = get_eje_config(eje_slug)
    desc = datos.get('descripcion_problema', '')[:80]
    if isinstance(desc, list):
        desc = ''
    tipo = (
        datos.get('tipo_enfermedad') or datos.get('tipo_atencion') or datos.get('tipo_problema')
        or datos.get('tipo_hecho') or datos.get('tipo_solicitud') or datos.get('tipo_incidente')
        or datos.get('tipo_situacion') or ''
    )
    if tipo:
        return f"{eje.get('nombre', eje_slug)} — {tipo}"
    return f"{eje.get('nombre', eje_slug)} — {desc[:60] if isinstance(desc, str) else ''}"


def _capturar_datos_form(request, eje_cfg):
    """Extrae y valida campos del formulario, incluyendo listas (medicamentos)."""
    datos = {}
    for campo in eje_cfg.get('campos', []):
        if campo.get('type') == 'checkbox_list':
            vals = request.POST.getlist(campo['name'])
            datos[campo['name']] = vals
            if campo.get('required') and not vals:
                return None, campo
        else:
            val = request.POST.get(campo['name'], '').strip()
            datos[campo['name']] = val
            if campo.get('required') and not val:
                return None, campo
            if campo.get('type') == 'centro_salud' and val:
                from geoespacial.models import PuntoAtencionEdomex
                municipio = datos.get('municipio', '').strip()
                qs = PuntoAtencionEdomex.objects.filter(slug=val, eje='salud')
                if municipio:
                    qs = qs.filter(municipio__iexact=municipio)
                if not qs.exists():
                    return None, campo
    return datos, None


def _datos_para_template(request_post):
    """Reconstruye datos POST para repoblar el formulario tras error."""
    datos = {}
    for key in request_post:
        if key in ('csrfmiddlewaretoken', 'accion', 'eje'):
            continue
        vals = request_post.getlist(key)
        datos[key] = vals if len(vals) > 1 else vals[0]
    return datos


@login_required
@requiere_publico
def portal_ciudadano_view(request):
    reportes = ReporteCiudadano.objects.filter(creado_por=request.user)[:10]
    return render(request, 'ciudadania/portal.html', {
        'reportes': reportes,
        'ejes': listar_ejes(),
    })


@login_required
@requiere_publico
def reporte_nuevo_view(request):
    eje_slug = request.GET.get('eje') or request.POST.get('eje')
    eje_cfg = get_eje_config(eje_slug) if eje_slug else None

    if 'sesion_ia' not in request.session:
        request.session['sesion_ia'] = nueva_sesion_asistente()

    sesion_key = request.session['sesion_ia']

    if request.method == 'POST' and request.POST.get('accion') == 'registrar':
        if not eje_slug or eje_slug not in EJES_CIUDADANIA:
            return redirect('ciudadania-nuevo')

        datos, campo_error = _capturar_datos_form(request, eje_cfg)
        if campo_error:
            return render(request, 'ciudadania/nuevo.html', {
                'ejes': listar_ejes(),
                'eje_slug': eje_slug,
                'eje_cfg': eje_cfg,
                'datos': _datos_para_template(request.POST),
                'sesion_key': sesion_key,
                'ubicaciones_json': ubicaciones_json(eje_slug),
                'entidad': ENTIDAD,
                'error': f'El campo "{campo_error["label"]}" es obligatorio.',
            })

        titulo = _titulo_desde_datos(eje_slug, datos)
        descripcion = datos.get('descripcion_problema', titulo)
        municipio = datos.get('municipio', '')

        if eje_slug == 'salud' and datos.get('centro_salud'):
            from geoespacial.models import PuntoAtencionEdomex
            cs = PuntoAtencionEdomex.objects.filter(slug=datos['centro_salud']).first()
            if cs:
                datos['centro_salud_nombre'] = cs.nombre
                datos['centro_salud_direccion'] = cs.direccion

        reporte = crear_reporte_ciudadano(
            request.user, eje_slug, titulo, descripcion, datos, municipio
        )
        if 'sesion_ia' in request.session:
            del request.session['sesion_ia']
        return redirect('ciudadania-detalle', pk=reporte.pk)

    mensajes_ia = MensajeReporteCiudadano.objects.filter(
        sesion_key=sesion_key, reporte__isnull=True
    ).order_by('creado_en')[:20]

    return render(request, 'ciudadania/nuevo.html', {
        'ejes': listar_ejes(),
        'eje_slug': eje_slug,
        'eje_cfg': eje_cfg,
        'datos': {},
        'sesion_key': sesion_key,
        'mensajes_ia': mensajes_ia,
        'ubicaciones_json': ubicaciones_json(eje_slug) if eje_slug else '[]',
        'entidad': ENTIDAD,
    })


@login_required
@requiere_publico
def reporte_detalle_view(request, pk):
    reporte = get_object_or_404(ReporteCiudadano, pk=pk, creado_por=request.user)
    mensajes = reporte.mensajes.all()
    ubicaciones = (
        obtener_centros_salud(reporte.municipio)
        if reporte.eje == 'salud'
        else obtener_ubicaciones_eje(reporte.eje, reporte.municipio)
    )
    return render(request, 'ciudadania/detalle.html', {
        'reporte': reporte,
        'mensajes': mensajes,
        'eje_cfg': reporte.eje_config,
        'ubicaciones': ubicaciones,
        'ubicaciones_json': json.dumps(ubicaciones, ensure_ascii=False),
        'centro_salud_slug': reporte.datos_captura.get('centro_salud', ''),
        'entidad': ENTIDAD,
    })


@login_required
@require_POST
def asistente_ia_api(request):
    """Chat con asistente IA (pre-registro)."""
    if obtener_rol(request.user) != 'publico':
        return JsonResponse({'error': 'No autorizado'}, status=403)

    try:
        body = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        body = request.POST

    mensaje = body.get('mensaje', '').strip()
    eje_slug = body.get('eje') or None
    fase = body.get('fase', 'exploracion')
    datos_parciales = body.get('datos', {})

    sesion_key = request.session.get('sesion_ia')
    if not sesion_key:
        sesion_key = nueva_sesion_asistente()
        request.session['sesion_ia'] = sesion_key

    if mensaje:
        registrar_mensaje(
            sesion_key=sesion_key,
            tipo_autor=MensajeReporteCiudadano.TipoAutor.CIUDADANO,
            autor_nombre=request.user.get_full_name() or request.user.username,
            contenido=mensaje,
        )

    if fase == 'bienvenida_eje' and eje_slug:
        respuesta = respuesta_asistente_ia('', eje_slug=eje_slug, fase='bienvenida_eje')
    elif not mensaje and not eje_slug:
        respuesta = mensaje_bienvenida_general()
    else:
        respuesta = respuesta_asistente_ia(mensaje, eje_slug=eje_slug, datos_parciales=datos_parciales, fase=fase)

    msg_ia = registrar_mensaje(
        sesion_key=sesion_key,
        tipo_autor=MensajeReporteCiudadano.TipoAutor.IA,
        autor_nombre='Asistente IA MITA',
        contenido=respuesta,
    )

    return JsonResponse({
        'respuesta': respuesta,
        'id': msg_ia.pk,
        'autor': 'Asistente IA MITA',
        'tipo': 'ia',
    })


@login_required
@require_POST
def reporte_chat_api(request, pk):
    """Chat ciudadano ↔ dependencia (simulado)."""
    reporte = get_object_or_404(ReporteCiudadano, pk=pk)
    rol = obtener_rol(request.user)

    if rol == 'publico' and reporte.creado_por_id != request.user.pk:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    if rol not in ('publico', 'dependencia', 'admin') and not request.user.is_superuser:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    try:
        body = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        body = request.POST

    mensaje = body.get('mensaje', '').strip()
    if not mensaje:
        return JsonResponse({'error': 'Mensaje vacío'}, status=400)

    autor = request.user.get_full_name() or request.user.username
    registrar_mensaje(
        reporte=reporte,
        tipo_autor=MensajeReporteCiudadano.TipoAutor.CIUDADANO,
        autor_nombre=autor,
        contenido=mensaje,
    )

    if reporte.estado == ReporteCiudadano.Estado.TURNADO:
        reporte.estado = ReporteCiudadano.Estado.EN_ATENCION
        reporte.save(update_fields=['estado', 'actualizado_en'])

    resp_dep = respuesta_dependencia_simulada(reporte, mensaje)
    msg_dep = registrar_mensaje(
        reporte=reporte,
        tipo_autor=MensajeReporteCiudadano.TipoAutor.DEPENDENCIA,
        autor_nombre=reporte.dependencia_principal,
        contenido=resp_dep,
    )

    return JsonResponse({
        'mensajes': [
            {'tipo': 'ciudadano', 'autor': autor, 'contenido': mensaje},
            {'tipo': 'dependencia', 'autor': reporte.dependencia_principal, 'contenido': resp_dep, 'id': msg_dep.pk},
        ],
        'estado': reporte.estado,
        'estado_label': reporte.get_estado_display(),
    })


@login_required
@require_GET
def centros_salud_api(request):
    """Lista de centros de salud ISSEM/SEDESA en Edomex, filtrable por municipio."""
    municipio = request.GET.get('municipio', '').strip() or None
    return JsonResponse({
        'entidad': ENTIDAD,
        'total': len(obtener_centros_salud(municipio)),
        'municipio': municipio,
        'centros': obtener_centros_salud(municipio),
    })


@login_required
@require_GET
def ubicaciones_eje_api(request, eje_slug):
    """Puntos de atención en Edomex filtrados por eje y municipio."""
    municipio = request.GET.get('municipio', '').strip() or None
    return JsonResponse({
        'entidad': ENTIDAD,
        'eje': eje_slug,
        'municipio': municipio,
        'ubicaciones': obtener_ubicaciones_eje(eje_slug, municipio),
    })


@login_required
@require_GET
def campos_eje_api(request, eje_slug):
    """Devuelve campos dinámicos del eje (JSON)."""
    cfg = get_eje_config(eje_slug)
    if not cfg:
        return JsonResponse({'error': 'Eje no encontrado'}, status=404)
    return JsonResponse({
        'eje': eje_slug,
        'nombre': cfg['nombre'],
        'campos': cfg['campos'],
        'dependencias': cfg['dependencias'],
    })
