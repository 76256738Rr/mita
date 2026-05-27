"""Permisos y roles de la Plataforma MITA."""

from functools import wraps

from django.contrib.auth.models import AnonymousUser

from core.models import PerfilUsuario

ROLES = {
    'admin': 4,
    'analista': 3,
    'investigador': 2,
    'dependencia': 1,
    'auditor': 1,
    'publico': 0,
}


def obtener_rol(usuario):
    if not usuario or isinstance(usuario, AnonymousUser) or not usuario.is_authenticated:
        return 'dependencia'
    if usuario.is_superuser:
        return 'admin'
    perfil = getattr(usuario, 'perfil_mita', None)
    return perfil.rol if perfil else 'dependencia'


def es_publico_general(usuario):
    return obtener_rol(usuario) == 'publico'


def requiere_publico(view_func):
    """Solo rol público general."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not es_publico_general(request.user) and not request.user.is_superuser:
            from django.contrib import messages
            from django.shortcuts import redirect
            messages.error(request, 'Esta sección es exclusiva para ciudadanos.')
            return redirect('bandeja')
        return view_func(request, *args, **kwargs)
    return wrapper


def rol_minimo(rol_requerido):
    """Decorador para vistas web que exigen un rol mínimo."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            rol = obtener_rol(request.user)
            if ROLES.get(rol, 0) < ROLES.get(rol_requerido, 0) and not request.user.is_superuser:
                from django.contrib import messages
                from django.shortcuts import redirect
                messages.error(request, 'No tiene permisos para esta acción.')
                return redirect('bandeja')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def puede_gestionar_expediente(usuario, expediente):
    rol = obtener_rol(usuario)
    if rol == 'auditor':
        return False
    if rol == 'admin' or usuario.is_superuser:
        return True
    if expediente.creado_por_id == usuario.pk or expediente.responsable_id == usuario.pk:
        return True
    paso_info = None
    from mita_engine.workflow import PASOS
    paso_info = PASOS.get(expediente.paso_actual, {})
    rol_paso = paso_info.get('rol', 'dependencia')
    return ROLES.get(rol, 0) >= ROLES.get(rol_paso, 0)


def puede_ver_expediente(usuario, expediente):
    """Auditor y roles autorizados pueden consultar expedientes."""
    rol = obtener_rol(usuario)
    if rol in ('admin', 'auditor') or usuario.is_superuser:
        return True
    return puede_gestionar_expediente(usuario, expediente)
