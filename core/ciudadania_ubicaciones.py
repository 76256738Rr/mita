"""Consulta de puntos de atención en el Estado de México por eje."""

import json

from geoespacial.models import PuntoAtencionEdomex


def obtener_ubicaciones_eje(eje_slug, municipio=None):
    """Puntos de atención filtrados por eje y opcionalmente municipio."""
    qs = PuntoAtencionEdomex.objects.filter(eje=eje_slug)
    if municipio:
        qs = qs.filter(municipio__iexact=municipio.strip())
    return [p.to_dict() for p in qs]


def obtener_centros_salud(municipio=None):
    """Catálogo de centros de salud ISSEM/SEDESA en Edomex."""
    qs = PuntoAtencionEdomex.objects.filter(eje='salud').order_by('municipio', 'nombre')
    if municipio:
        qs = qs.filter(municipio__iexact=municipio.strip())
    return [p.to_dict() for p in qs]


def ubicaciones_json(eje_slug, municipio=None):
    return json.dumps(obtener_ubicaciones_eje(eje_slug, municipio), ensure_ascii=False)


def centros_salud_json(municipio=None):
    return json.dumps(obtener_centros_salud(municipio), ensure_ascii=False)
