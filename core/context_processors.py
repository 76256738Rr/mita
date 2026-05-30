from django.conf import settings

from core.permissions import obtener_rol
from core.navigation import menu_para_rol
from mita_engine.proceso_utils import metricas_proceso_operativo


def mita_context(request):
    ctx = {'MITA': settings.MITA_PLATFORM}
    path = request.path
    if request.user.is_authenticated:
        ctx['user_rol'] = obtener_rol(request.user)
        ctx['menu_navegacion'] = menu_para_rol(ctx['user_rol'], path)
    else:
        ctx['user_rol'] = None
        ctx['menu_navegacion'] = []
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
