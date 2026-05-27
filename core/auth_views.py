from django.contrib.auth.views import LoginView
from django.shortcuts import resolve_url

from core.demo_simulation import DEMO_FOLIO_ACTIVO, DEMO_FOLIO_DICTAMINADO, PASSWORD_DEMO, USUARIOS_DEMO
from core.permissions import obtener_rol
from mita_engine.models import Expediente


class MitaLoginView(LoginView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['usuarios_demo'] = USUARIOS_DEMO
        ctx['password_demo'] = PASSWORD_DEMO
        ctx['rol_seleccionado'] = self.request.GET.get('rol', '')
        if ctx['rol_seleccionado']:
            match = next((u for u in USUARIOS_DEMO if u['username'] == ctx['rol_seleccionado']), None)
            if match:
                ctx['username_prefill'] = match['username']
        return ctx

    def get_success_url(self):
        rol = obtener_rol(self.request.user)
        activo = Expediente.objects.filter(folio=DEMO_FOLIO_ACTIVO).first()
        dictaminado = Expediente.objects.filter(folio=DEMO_FOLIO_DICTAMINADO).first()

        if rol == 'investigador' and activo:
            return resolve_url('expediente-detalle', pk=activo.pk)
        if rol == 'admin' and activo:
            return resolve_url('expediente-detalle', pk=activo.pk)
        if rol == 'analista' and activo:
            return resolve_url('expediente-detalle', pk=activo.pk)
        if rol == 'dependencia':
            return resolve_url('expediente-nuevo')
        if rol == 'auditor' and dictaminado:
            return resolve_url('expediente-detalle', pk=dictaminado.pk)
        if rol == 'publico':
            return resolve_url('ciudadania-portal')
        return resolve_url('bandeja')
