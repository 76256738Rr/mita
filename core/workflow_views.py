"""Vistas del motor de procesos y flujos MITA."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from conocimiento.models import Disciplina
from core.forms import ComentarioAvanceForm, ExpedienteNuevoForm, Paso1Form, Paso4Form, Paso6Form
from core.permissions import puede_gestionar_expediente, puede_ver_expediente
from geoespacial.models import ZonaGeografica
from interculturalidad.models import SaberTradicional
from mita_engine.models import CruceInterdisciplinario, Expediente, PasoProceso
from mita_engine.proceso_utils import contexto_herramientas, estado_proceso_expediente
from mita_engine.workflow import PASOS, WorkflowEngine, WorkflowError


def _parse_paso4(request):
    return {
        'titulo': request.POST.get('titulo', ''),
        'descripcion': request.POST.get('descripcion', ''),
        'solicitante': request.POST.get('solicitante', ''),
        'marco_legal': 'marco_legal' in request.POST,
        'derechos_humanos': 'derechos_humanos' in request.POST,
        'normativa_aplicable': 'normativa_aplicable' in request.POST,
        'recursos_tecnicos': 'recursos_tecnicos' in request.POST,
        'infraestructura': 'infraestructura' in request.POST,
        'plazo_ejecucion': 'plazo_ejecucion' in request.POST,
        'presupuesto': float(request.POST.get('presupuesto', 0) or 0),
        'retorno_inversion': 'retorno_inversion' in request.POST,
        'sostenibilidad': 'sostenibilidad' in request.POST,
        'beneficiarios': 'beneficiarios' in request.POST,
        'necesidad_identificada': 'necesidad_identificada' in request.POST,
        'impacto_esperado': 'impacto_esperado' in request.POST,
        'enfoque_integral': 'enfoque_integral' in request.POST,
        'adaptacion_cultural': 'adaptacion_cultural' in request.POST,
        'interculturalidad': 'interculturalidad' in request.POST,
        'ejes_accion': [int(x) for x in request.POST.getlist('ejes_accion') if x.isdigit()],
    }


@login_required
def bandeja_view(request):
    tareas = WorkflowEngine.bandeja(request.user)
    expedientes_activos = Expediente.objects.exclude(
        estado__in=[Expediente.Estado.CERRADO, Expediente.Estado.CANCELADO],
    ).order_by('-actualizado_en')[:20]
    return render(request, 'bandeja.html', {
        'tareas': tareas,
        'expedientes': expedientes_activos,
        'total_tareas': tareas.count(),
    })


@login_required
def expedientes_list_view(request):
    estado = request.GET.get('estado')
    qs = Expediente.objects.all()
    if estado:
        qs = qs.filter(estado=estado)
    return render(request, 'expedientes/lista.html', {
        'expedientes': qs[:50],
        'estados': Expediente.Estado.choices,
        'estado_filtro': estado,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def expediente_nuevo_view(request):
    form = ExpedienteNuevoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            exp = WorkflowEngine.crear_expediente(
                request.user,
                titulo=form.cleaned_data['titulo'],
                descripcion=form.cleaned_data.get('descripcion', ''),
                solicitante=form.cleaned_data.get('solicitante', ''),
                dependencia=form.cleaned_data.get('dependencia', ''),
            )
            messages.success(request, f'Expediente {exp.folio} creado. Complete el paso 1.')
            return redirect('expediente-detalle', pk=exp.pk)
        except WorkflowError as e:
            messages.error(request, str(e))
    return render(request, 'expedientes/nuevo.html', {'form': form})


@login_required
@require_http_methods(['GET', 'POST'])
def expediente_detalle_view(request, pk):
    expediente = get_object_or_404(
        Expediente.objects.select_related('propuesta', 'creado_por', 'responsable'),
        pk=pk,
    )
    if not puede_ver_expediente(request.user, expediente):
        messages.error(request, 'No tiene permisos para ver este expediente.')
        return redirect('bandeja')

    solo_lectura = not puede_gestionar_expediente(request.user, expediente)

    request.session['expediente_activo'] = expediente.pk
    paso = expediente.paso_actual
    comentario_form = ComentarioAvanceForm()
    pasos_catalogo = list(PasoProceso.objects.all())
    pasos_info = PASOS

    if request.method == 'POST':
        if solo_lectura:
            messages.error(request, 'Su rol solo permite consulta. No puede modificar expedientes.')
            return redirect('expediente-detalle', pk=pk)
        accion = request.POST.get('accion')

        try:
            if accion == 'guardar':
                if paso == 1:
                    datos = {
                        'titulo': request.POST.get('titulo', expediente.titulo),
                        'descripcion': request.POST.get('descripcion', ''),
                        'solicitante': request.POST.get('solicitante', ''),
                        'dependencia': request.POST.get('dependencia', ''),
                    }
                    WorkflowEngine.guardar_paso(expediente, 1, datos, request.user)
                elif paso == 2:
                    ids = request.POST.getlist('disciplinas')
                    WorkflowEngine.guardar_paso(expediente, 2, {'disciplinas_ids': ids}, request.user)
                elif paso == 3:
                    datos = {
                        'confirmado': True,
                        'zonas_ids': request.POST.getlist('zonas'),
                        'saberes_ids': [int(x) for x in request.POST.getlist('saberes') if x.isdigit()],
                        'cruces_catalogo': request.POST.getlist('cruces_catalogo'),
                    }
                    WorkflowEngine.guardar_paso(expediente, 3, datos, request.user)
                elif paso == 4:
                    criterios = _parse_paso4(request)
                    criterios['titulo'] = expediente.titulo
                    criterios['descripcion'] = expediente.descripcion
                    criterios['solicitante'] = expediente.solicitante
                    WorkflowEngine.guardar_paso(expediente, 4, criterios, request.user)
                elif paso == 6:
                    opcion_id = int(request.POST.get('opcion_id', 0))
                    WorkflowEngine.guardar_paso(expediente, 6, {'opcion_id': opcion_id}, request.user)
                messages.success(request, f'Paso {paso} guardado.')
                expediente.refresh_from_db()

            elif accion == 'avanzar':
                comentario = request.POST.get('comentario', '')
                WorkflowEngine.avanzar(expediente, request.user, comentario)
                messages.success(request, f'Expediente avanzó al paso {expediente.paso_actual + 1 if paso < 7 else 7}.')
                return redirect('expediente-detalle', pk=pk)

            elif accion == 'dictaminar' and paso == 7:
                WorkflowEngine.emitir_dictamen(expediente, request.user)
                messages.success(request, 'Dictamen MITA emitido correctamente.')
                return redirect('expediente-detalle', pk=pk)

            elif accion == 'seguimiento':
                WorkflowEngine.iniciar_seguimiento(expediente, request.user, request.POST.get('comentario', ''))
                messages.success(request, 'Expediente en seguimiento.')
                return redirect('expediente-detalle', pk=pk)

        except WorkflowError as e:
            messages.error(request, str(e))

        expediente.refresh_from_db()
        paso = expediente.paso_actual

    cruce = (expediente.artefactos or {}).get('3', {}).get('cruce')
    artefacto3 = (expediente.artefactos or {}).get('3', {})
    dictamen = None
    if expediente.propuesta_id:
        dictamen = getattr(expediente.propuesta, 'dictamen', None)

    return render(request, 'expedientes/detalle.html', {
        'expediente': expediente,
        'paso': paso,
        'pasos_catalogo': pasos_catalogo,
        'pasos_info': pasos_info,
        'pasos_estado': estado_proceso_expediente(expediente),
        'ctx_herramientas': contexto_herramientas(expediente, paso),
        'disciplinas': Disciplina.objects.filter(activo=True),
        'disciplinas_sel': set(expediente.disciplinas_ids or []),
        'zonas': ZonaGeografica.objects.all(),
        'zonas_sel': set(artefacto3.get('zonas_ids', [])),
        'saberes': SaberTradicional.objects.filter(validado=True),
        'saberes_sel': set(artefacto3.get('saberes_ids', [])),
        'cruces_catalogo': CruceInterdisciplinario.objects.all(),
        'cruces_sel': set(str(x) for x in artefacto3.get('cruces_catalogo', [])),
        'opciones': expediente.opciones.all(),
        'evaluacion': expediente.evaluacion,
        'cruce': cruce,
        'dictamen': dictamen,
        'historial': WorkflowEngine.historial(expediente),
        'comentario_form': comentario_form,
        'artefacto_paso4': (expediente.artefactos or {}).get('4', {}).get('criterios', {}),
        'solo_lectura': solo_lectura,
        'es_demo': expediente.folio.startswith('MITA-DEMO'),
    })
