import json

from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.views import View
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from conocimiento.models import Disciplina
from geoespacial.models import ZonaGeografica
from core.analogia_utils import CRITERIO_ICONOS, CRITERIOS_LABELS, propuesta_desde_post, persistir_dictamen
from core.demo_simulation import CRITERIOS_DEMO, DEMO_FOLIO_ACTIVO, DEMO_FOLIO_DICTAMINADO
from mita_engine.models import CruceInterdisciplinario, Dictamen, EjeMITA, Expediente, PasoProceso, TareaExpediente
from mita_engine.proceso_utils import metricas_proceso_operativo
from mita_engine.services import evaluar_analogia, generar_dictamen
from mita_engine.workflow import WorkflowEngine
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
    """Motor Analógico MITA — evaluación de propuestas y dictamen (RF-06)."""
    from django.contrib import messages

    expediente = _expediente_from_request(request)
    propuesta = {}
    resultado = None
    dictamen = None
    dictamen_obj = None

    if request.method == 'POST':
        propuesta = propuesta_desde_post(request.POST)
        if not propuesta.get('titulo'):
            messages.error(request, 'Indique el título de la propuesta.')
        else:
            resultado = evaluar_analogia(propuesta)

            if expediente and expediente.paso_actual == 4:
                try:
                    WorkflowEngine.guardar_paso(expediente, 4, propuesta, request.user)
                    messages.success(
                        request,
                        f'Evaluación analógica guardada en expediente {expediente.folio} (Paso 4).',
                    )
                except Exception as exc:
                    messages.warning(request, f'No se pudo vincular al expediente: {exc}')

            if request.POST.get('generar_dictamen'):
                dictamen, dictamen_obj = persistir_dictamen(
                    propuesta, resultado, request.user
                )
                messages.success(request, f'Dictamen {dictamen["folio"]} generado y registrado.')
            else:
                messages.success(request, 'Evaluación analógica completada.')

    elif request.GET.get('demo') == '1':
        propuesta = dict(CRITERIOS_DEMO)
        propuesta['ejes_accion'] = list(CRITERIOS_DEMO.get('ejes_accion', []))

    elif expediente:
        paso1 = (expediente.artefactos or {}).get('1', {})
        paso4 = (expediente.artefactos or {}).get('4', {})
        if paso4.get('criterios'):
            propuesta = paso4['criterios']
            resultado = paso4.get('evaluacion')
        elif paso1:
            propuesta = {
                'titulo': paso1.get('titulo', expediente.titulo),
                'descripcion': paso1.get('descripcion', expediente.descripcion),
                'solicitante': paso1.get('solicitante', expediente.solicitante),
                'presupuesto': 0,
                'ejes_accion': [],
            }

    criterios_visual = []
    riesgos_visual = []
    if resultado:
        for clave, valor in resultado.get('criterios', {}).items():
            criterios_visual.append({
                'clave': clave,
                'nombre': CRITERIOS_LABELS.get(clave, clave.replace('_', ' ').title()),
                'valor': valor,
                'icono': CRITERIO_ICONOS.get(clave, 'img/analogia/criterio-coherencia.svg'),
            })
        from core.analogia_utils import RIESGO_ICONOS
        for riesgo in resultado.get('riesgos', []):
            riesgos_visual.append({
                **riesgo,
                'icono': RIESGO_ICONOS.get(riesgo.get('tipo'), 'img/analogia/riesgo-sesgado.svg'),
            })

    if propuesta.get('ejes_accion'):
        propuesta = {**propuesta, 'ejes_str': [str(x) for x in propuesta['ejes_accion']]}

    return render(request, 'analogia.html', {
        'expediente': expediente,
        'propuesta': propuesta,
        'resultado': resultado,
        'dictamen': dictamen,
        'dictamen_obj': dictamen_obj,
        'criterios_visual': criterios_visual,
        'riesgos_visual': riesgos_visual,
        'paso_proceso': 4,
    })


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


class MitaLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("login")

    def post(self, request):
        logout(request)
        return redirect("login")
