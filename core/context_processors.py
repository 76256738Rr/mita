from django.conf import settings

from core.permissions import obtener_rol
from mita_engine.proceso_utils import metricas_proceso_operativo


def mita_context(request):
    ctx = {'MITA': settings.MITA_PLATFORM}
    if request.user.is_authenticated:
        ctx['user_rol'] = obtener_rol(request.user)
    else:
        ctx['user_rol'] = None
    try:
        ctx['proceso_metricas'] = metricas_proceso_operativo()
    except Exception:
        ctx['proceso_metricas'] = None

    expediente_id = request.GET.get('expediente') or request.session.get('expediente_activo')
    if expediente_id:
        from mita_engine.models import Expediente
        try:
            ctx['expediente_activo'] = Expediente.objects.get(pk=expediente_id)
        except (Expediente.DoesNotExist, ValueError):
            ctx['expediente_activo'] = None
    else:
        ctx['expediente_activo'] = None
    return ctx
