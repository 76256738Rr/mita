import json

from django.contrib.auth.views import LogoutView
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from conocimiento.models import Disciplina
from geoespacial.models import ZonaGeografica
from core.demo_simulation import DEMO_FOLIO_ACTIVO, DEMO_FOLIO_DICTAMINADO
from mita_engine.models import CruceInterdisciplinario, Dictamen, EjeMITA, Expediente, PasoProceso, TareaExpediente
from mita_engine.proceso_utils import metricas_proceso_operativo
from mita_engine.services import evaluar_analogia, generar_dictamen
from proyectos.models import ProyectoReferencia
from reportes.models import IndicadorImpacto
from sni.models import PerfilSNI


def _expediente_from_request(request):
    exp_id = request.GET.get('expediente')
    if exp_id:
        try:
            return Expediente.objects.get(pk=exp_id)
        except (Expediente.DoesNotExist, ValueError):
            pass
    return None


def dashboard_view(request):
    proyecto = ProyectoReferencia.objects.filter(activo=True).first()
    expedientes_activos = Expediente.objects.exclude(
        estado__in=[Expediente.Estado.CERRADO, Expediente.Estado.CANCELADO],
    ).count()
    return render(request, 'dashboard.html', {
        'proyecto': proyecto,
        'stats': {
            'disciplinas': Disciplina.objects.filter(activo=True).count(),
            'zonas': ZonaGeografica.objects.count(),
            'cruces': CruceInterdisciplinario.objects.count(),
            'dictamenes': Dictamen.objects.count(),
            'expedientes': expedientes_activos,
            'tareas': TareaExpediente.objects.filter(completada=False).count(),
        },
        'expedientes_recientes': Expediente.objects.order_by('-actualizado_en')[:5],
        'proceso': metricas_proceso_operativo(),
        'demo_activo': Expediente.objects.filter(folio=DEMO_FOLIO_ACTIVO).first(),
        'demo_dictaminado': Expediente.objects.filter(folio=DEMO_FOLIO_DICTAMINADO).first(),
    })


def base_datos_view(request):
    disciplinas = Disciplina.objects.filter(activo=True)
    grupo = request.GET.get('grupo')
    if grupo:
        disciplinas = disciplinas.filter(grupo=grupo)
    expediente = _expediente_from_request(request)
    paso = int(request.GET.get('paso', 2))
    return render(request, 'base_datos.html', {
        'disciplinas': disciplinas,
        'expediente': expediente,
        'paso_proceso': paso,
        'modo_seleccion': expediente and paso == 2,
    })


def mapa_view(request):
    zonas = ZonaGeografica.objects.all()
    expediente = _expediente_from_request(request)
    return render(request, 'mapa.html', {
        'zonas_json': json.dumps([z.to_dict() for z in zonas]),
        'zonas': zonas,
        'expediente': expediente,
        'paso_proceso': int(request.GET.get('paso', 3)),
    })


def metodologia_view(request):
    return render(request, 'metodologia.html', {
        'ejes': EjeMITA.objects.all(),
    })


def proceso_view(request):
    metricas = metricas_proceso_operativo()
    return render(request, 'proceso.html', {
        'metricas': metricas,
        'pasos': metricas['pasos'],
        'cruces': CruceInterdisciplinario.objects.all()[:5],
    })


def proyecto_view(request):
    proyecto = ProyectoReferencia.objects.filter(activo=True).first()
    ejes = proyecto.ejes_accion.all() if proyecto else []
    return render(request, 'proyecto.html', {
        'proyecto': proyecto,
        'ejes': ejes,
    })


@require_http_methods(['GET', 'POST'])
def analogia_view(request):
    """Redirige al flujo de expediente (paso 4 del proceso operativo)."""
    from django.contrib import messages
    from django.shortcuts import redirect

    expediente = _expediente_from_request(request)
    if not expediente:
        activos = Expediente.objects.filter(paso_actual=4).exclude(
            estado__in=[Expediente.Estado.CERRADO, Expediente.Estado.CANCELADO],
        ).order_by('-actualizado_en')
        expediente = activos.first()

    if expediente:
        if request.user.is_authenticated:
            request.session['expediente_activo'] = expediente.pk
        messages.info(request, f'Análisis analógico integrado en el expediente {expediente.folio} (Paso 4).')
        return redirect('expediente-detalle', pk=expediente.pk)

    messages.warning(request, 'Cree un expediente para iniciar el proceso operativo.')
    return redirect('expediente-nuevo')


def sni_view(request):
    expediente = _expediente_from_request(request)
    return render(request, 'sni.html', {
        'perfiles': PerfilSNI.objects.filter(activo=True),
        'expediente': expediente,
        'paso_proceso': int(request.GET.get('paso', 6)),
    })


def reportes_view(request):
    return render(request, 'reportes.html', {
        'indicadores': IndicadorImpacto.objects.all(),
    })


def dictamenes_view(request):
    return render(request, 'dictamenes.html', {
        'dictamenes': Dictamen.objects.select_related('propuesta').all()[:30],
    })


class MitaLogoutView(LogoutView):
    next_page = '/login/'
