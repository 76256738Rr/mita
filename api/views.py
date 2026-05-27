from django.core.files.base import ContentFile
from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from conocimiento.models import Disciplina, FuenteInformacion
from core.models import RegistroAuditoria
from geoespacial.models import CapaGeografica, ZonaGeografica
from interculturalidad.models import SaberTradicional
from mita_engine.models import CruceInterdisciplinario, Dictamen, EjeMITA, Expediente, PasoProceso, PropuestaEvaluacion
from mita_engine.workflow import WorkflowEngine, WorkflowError
from mita_engine.pdf import generar_pdf_dictamen
from mita_engine.services import (
    analizar_impacto_normativo,
    calcular_cruce,
    comparar_cultural_cientifico,
    evaluar_analogia,
    generar_dictamen,
    sintesis_transdisciplinaria,
)
from proyectos.models import EjeAccion, LeccionAprendida, ProyectoReferencia
from reportes.models import IndicadorImpacto
from sni.models import InvestigadorSNI, PerfilSNI

from .serializers import CruceRequestSerializer, PropuestaEvaluacionSerializer


def _disciplinas_db():
    return [d.to_dict() for d in Disciplina.objects.filter(activo=True)]


def _registrar_auditoria(request, accion, entidad, entidad_id='', detalle=None):
    RegistroAuditoria.objects.create(
        usuario=request.user if request.user.is_authenticated else None,
        accion=accion,
        entidad=entidad,
        entidad_id=str(entidad_id),
        detalle=detalle or {},
        ip_address=request.META.get('REMOTE_ADDR'),
    )


@api_view(['GET'])
def health(request):
    return Response({'status': 'ok', 'plataforma': 'MITA', 'version': '1.0.0'})


@api_view(['GET'])
def dashboard(request):
    proyecto = ProyectoReferencia.objects.filter(activo=True).first()
    return Response({
        'plataforma': 'MITA — Multi-intercultural-transdisciplina Analógica',
        'subtitulo': 'Herramienta Oficial de Gestión del Conocimiento y Buen Gobierno',
        'proyecto_demo': proyecto.nombre if proyecto else '',
        'estadisticas': {
            'disciplinas': Disciplina.objects.filter(activo=True).count(),
            'zonas_geograficas': ZonaGeografica.objects.count(),
            'cruces_interdisciplinarios': CruceInterdisciplinario.objects.count(),
            'ejes_accion': EjeAccion.objects.count(),
            'perfiles_snii': PerfilSNI.objects.filter(activo=True).count(),
            'saberes_tradicionales': SaberTradicional.objects.filter(validado=True).count(),
            'fuentes_validadas': FuenteInformacion.objects.filter(activa=True).count(),
            'dictamenes_emitidos': Dictamen.objects.count(),
        },
        'indicadores_salud': proyecto.indicadores if proyecto else {},
        'metas': proyecto.metas_globales if proyecto else {},
    })


@api_view(['GET'])
def disciplinas_list(request):
    qs = Disciplina.objects.filter(activo=True)
    grupo = request.query_params.get('grupo')
    area = request.query_params.get('area')
    if grupo:
        qs = qs.filter(grupo=grupo)
    if area:
        qs = qs.filter(area__icontains=area)
    data = [d.to_dict() for d in qs]
    return Response({'total': len(data), 'disciplinas': data})


@api_view(['GET'])
def disciplina_detail(request, disciplina_id):
    try:
        d = Disciplina.objects.get(slug=disciplina_id, activo=True)
        return Response(d.to_dict())
    except Disciplina.DoesNotExist:
        return Response({'detail': 'Disciplina no encontrada'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def fuentes_list(request):
    fuentes = FuenteInformacion.objects.filter(activa=True)
    return Response({
        'total': fuentes.count(),
        'fuentes': [
            {
                'nombre': f.nombre,
                'tipo': f.tipo,
                'nivel_confiabilidad': f.nivel_confiabilidad,
            }
            for f in fuentes
        ],
    })


@api_view(['GET'])
def zonas_list(request):
    qs = ZonaGeografica.objects.all()
    tipo = request.query_params.get('tipo')
    corredor = request.query_params.get('corredor')
    if tipo:
        qs = qs.filter(tipo=tipo)
    if corredor:
        qs = qs.filter(corredor=corredor)
    data = [z.to_dict() for z in qs]
    return Response({'total': len(data), 'zonas': data})


@api_view(['GET'])
def capas_geo(request):
    return Response({'capas': [c.to_dict() for c in CapaGeografica.objects.all()]})


@api_view(['GET'])
def resumen_geoespacial(request):
    hotspots = ZonaGeografica.objects.filter(tipo='hotspot')
    count = hotspots.count()
    avg = round(sum(z.prevalencia for z in hotspots) / count, 1) if count else 0
    return Response({
        'hotspots': count,
        'prevalencia_promedio_hotspots': avg,
        'corredores': {
            'oriente': ZonaGeografica.objects.filter(corredor='oriente').count(),
            'conurbada': ZonaGeografica.objects.filter(corredor='conurbada').count(),
            'indigena': ZonaGeografica.objects.filter(corredor='indigena').count(),
            'poniente': ZonaGeografica.objects.filter(corredor='poniente').count(),
        },
        'conclusion': (
            'El problema no es uniforme: está concentrado en zonas con mayor desigualdad, '
            'mala infraestructura y hábitos alimentarios dañinos.'
        ),
    })


@api_view(['GET'])
def ejes_mita(request):
    return Response({'ejes': [e.to_dict() for e in EjeMITA.objects.all()]})


@api_view(['GET'])
def proceso_mita(request):
    from mita_engine.proceso_utils import metricas_proceso_operativo
    metricas = metricas_proceso_operativo()
    return Response({
        'pasos': [
            {
                **p,
                'expedientes': [e.to_dict() for e in p['expedientes']],
            }
            for p in metricas['pasos']
        ],
        'metricas': {
            'total_activos': metricas['total_activos'],
            'total_dictaminados': metricas['total_dictaminados'],
        },
    })


@api_view(['GET'])
def cruces_list(request):
    return Response({'cruces': [c.to_dict() for c in CruceInterdisciplinario.objects.all()]})


@api_view(['POST'])
def cruce_create(request):
    serializer = CruceRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    result = calcular_cruce(serializer.validated_data['disciplina_ids'], _disciplinas_db())
    if 'error' in result:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    _registrar_auditoria(request, 'CRUCE_INTERDISCIPLINARIO', 'Disciplina', detalle=result)
    return Response(result)


@api_view(['POST'])
def analogia_evaluar(request):
    serializer = PropuestaEvaluacionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    evaluacion = evaluar_analogia(data)
    _registrar_auditoria(request, 'EVALUAR_ANALOGIA', 'Propuesta', data.get('titulo', ''), evaluacion)
    return Response({'propuesta': data['titulo'], 'evaluacion': evaluacion})


@api_view(['POST'])
def dictamen_generar(request):
    serializer = PropuestaEvaluacionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    evaluacion = evaluar_analogia(data)
    dictamen_data = generar_dictamen(data, evaluacion, data.get('solicitante', ''))

    propuesta = PropuestaEvaluacion.objects.create(
        titulo=data['titulo'],
        descripcion=data.get('descripcion', ''),
        solicitante=data.get('solicitante', ''),
        estado=PropuestaEvaluacion.Estado.DICTAMINADO,
        criterios=data,
        puntuacion_total=evaluacion['puntuacion_total'],
        aprobado=evaluacion['aprobado'],
        creado_por=request.user if request.user.is_authenticated else None,
    )

    pdf_buffer = generar_pdf_dictamen(dictamen_data)
    dictamen_obj = Dictamen.objects.create(
        propuesta=propuesta,
        folio=dictamen_data['folio'],
        resultado=dictamen_data['resultado'],
        puntuacion=dictamen_data['puntuacion'],
        nivel_fronesis=dictamen_data['nivel_fronesis'],
        evaluacion_completa={'evaluacion': evaluacion, 'dictamen': dictamen_data},
    )
    dictamen_obj.pdf_archivo.save(
        f"{dictamen_data['folio']}.pdf",
        ContentFile(pdf_buffer.read()),
        save=True,
    )

    _registrar_auditoria(request, 'GENERAR_DICTAMEN', 'Dictamen', dictamen_data['folio'], dictamen_data)
    return Response({'evaluacion': evaluacion, 'dictamen': dictamen_data, 'dictamen_id': dictamen_obj.pk})


@api_view(['GET'])
def dictamen_pdf(request, dictamen_id):
    try:
        d = Dictamen.objects.get(pk=dictamen_id)
        if not d.pdf_archivo:
            return Response({'detail': 'PDF no disponible'}, status=status.HTTP_404_NOT_FOUND)
        return FileResponse(d.pdf_archivo.open('rb'), content_type='application/pdf', filename=f'{d.folio}.pdf')
    except Dictamen.DoesNotExist:
        return Response({'detail': 'Dictamen no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def dictamenes_list(request):
    return Response({
        'total': Dictamen.objects.count(),
        'dictamenes': [
            {
                'id': d.pk,
                'folio': d.folio,
                'asunto': d.propuesta.titulo,
                'resultado': d.resultado,
                'puntuacion': d.puntuacion,
                'emitido_en': d.emitido_en.isoformat(),
            }
            for d in Dictamen.objects.select_related('propuesta').all()[:50]
        ],
    })


@api_view(['GET'])
def proyecto_detail(request):
    proyecto = ProyectoReferencia.objects.filter(activo=True).first()
    if not proyecto:
        return Response({'detail': 'Proyecto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    return Response({
        'nombre': proyecto.nombre,
        'objetivo': proyecto.objetivo,
        'enfoque': proyecto.enfoque,
        'analogia': proyecto.analogia,
        'metas_globales': proyecto.metas_globales,
        'indicadores': proyecto.indicadores,
    })


@api_view(['GET'])
def ejes_accion(request):
    proyecto = ProyectoReferencia.objects.filter(activo=True).first()
    ejes = proyecto.ejes_accion.all() if proyecto else EjeAccion.objects.none()
    return Response({'ejes': [e.to_dict() for e in ejes]})


@api_view(['GET'])
def perfiles_sni(request):
    return Response({'perfiles': [p.to_dict() for p in PerfilSNI.objects.filter(activo=True)]})


@api_view(['GET'])
def investigadores_sni(request):
    qs = InvestigadorSNI.objects.filter(disponible=True)
    area = request.query_params.get('area')
    if area:
        qs = qs.filter(area_especialidad__icontains=area)
    return Response({
        'total': qs.count(),
        'investigadores': [
            {
                'id': i.pk,
                'nombre': i.nombre,
                'area': i.area_especialidad,
                'nivel': i.nivel_snii,
                'institucion': i.institucion,
            }
            for i in qs
        ],
    })


@api_view(['GET'])
def sintesis(request):
    proyecto = ProyectoReferencia.objects.filter(activo=True).first()
    data = sintesis_transdisciplinaria(
        Disciplina.objects.filter(activo=True),
        CruceInterdisciplinario.objects.all(),
    )
    if proyecto:
        data['analogia'] = proyecto.analogia
    return Response(data)


@api_view(['GET'])
def saberes_tradicionales(request):
    qs = SaberTradicional.objects.filter(validado=True)
    comunidad = request.query_params.get('comunidad')
    if comunidad:
        qs = qs.filter(comunidad=comunidad)
    return Response({'total': qs.count(), 'saberes': [s.to_dict() for s in qs]})


@api_view(['POST'])
def comparador_cultural(request):
    saber_id = request.data.get('saber_id')
    enfoque = request.data.get('enfoque_cientifico', 'Tratamiento farmacológico estándar')
    try:
        saber = SaberTradicional.objects.get(pk=saber_id)
        return Response(comparar_cultural_cientifico(saber.titulo, enfoque))
    except SaberTradicional.DoesNotExist:
        return Response({'detail': 'Saber no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def analisis_legislativo(request):
    serializer = PropuestaEvaluacionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(analizar_impacto_normativo(serializer.validated_data))


@api_view(['GET'])
def indicadores_impacto(request):
    sector = request.query_params.get('sector')
    qs = IndicadorImpacto.objects.all()
    if sector:
        qs = qs.filter(sector=sector)
    return Response({'indicadores': [i.to_dict() for i in qs]})


@api_view(['GET'])
def lecciones_aprendidas(request):
    qs = LeccionAprendida.objects.all()
    sector = request.query_params.get('sector')
    if sector:
        qs = qs.filter(sector=sector)
    return Response({
        'total': qs.count(),
        'lecciones': [
            {
                'titulo': l.titulo,
                'sector': l.sector,
                'institucion': l.institucion,
                'descripcion': l.descripcion,
                'impacto_medido': l.impacto_medido,
                'anio': l.anio,
            }
            for l in qs
        ],
    })


@api_view(['GET'])
def buscar_semantica(request):
    """Búsqueda semántica básica (RF-02) sobre disciplinas y saberes."""
    from django.db.models import Q

    q = request.query_params.get('q', '').strip()
    if not q:
        return Response({'detail': 'Parámetro q requerido'}, status=status.HTTP_400_BAD_REQUEST)
    disciplinas = Disciplina.objects.filter(activo=True).filter(
        Q(nombre__icontains=q) |
        Q(area__icontains=q) |
        Q(aportacion__icontains=q) |
        Q(dato_clave__icontains=q)
    )
    saberes = SaberTradicional.objects.filter(validado=True).filter(
        Q(titulo__icontains=q) |
        Q(descripcion__icontains=q)
    )
    return Response({
        'consulta': q,
        'disciplinas': [d.to_dict() for d in disciplinas[:20]],
        'saberes': [s.to_dict() for s in saberes[:10]],
        'total': disciplinas.count() + saberes.count(),
    })


@api_view(['GET', 'POST'])
def expedientes_list_create(request):
    if request.method == 'GET':
        estado = request.query_params.get('estado')
        qs = Expediente.objects.all()
        if estado:
            qs = qs.filter(estado=estado)
        return Response({
            'total': qs.count(),
            'expedientes': [e.to_dict() for e in qs[:50]],
        })

    titulo = request.data.get('titulo', '').strip()
    if not titulo:
        return Response({'detail': 'titulo requerido'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        exp = WorkflowEngine.crear_expediente(
            request.user,
            titulo=titulo,
            descripcion=request.data.get('descripcion', ''),
            solicitante=request.data.get('solicitante', ''),
            dependencia=request.data.get('dependencia', ''),
        )
        return Response(exp.to_dict(), status=status.HTTP_201_CREATED)
    except WorkflowError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def expediente_detail_api(request, pk):
    try:
        exp = Expediente.objects.get(pk=pk)
    except Expediente.DoesNotExist:
        return Response({'detail': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)
    data = exp.to_dict()
    data['historial'] = [
        {
            'paso_anterior': t.paso_anterior,
            'paso_nuevo': t.paso_nuevo,
            'accion': t.accion,
            'comentario': t.comentario,
            'fecha': t.creado_en.isoformat(),
        }
        for t in exp.transiciones.all()
    ]
    data['tareas_pendientes'] = exp.tareas.filter(completada=False).count()
    data['opciones'] = [
        {'id': o.pk, 'titulo': o.titulo, 'puntuacion': o.puntuacion, 'seleccionada': o.seleccionada}
        for o in exp.opciones.all()
    ]
    return Response(data)


@api_view(['POST'])
def expediente_avanzar(request, pk):
    try:
        exp = Expediente.objects.get(pk=pk)
        WorkflowEngine.avanzar(exp, request.user, request.data.get('comentario', ''))
        return Response(exp.to_dict())
    except Expediente.DoesNotExist:
        return Response({'detail': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except WorkflowError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def expediente_guardar_paso(request, pk):
    try:
        exp = Expediente.objects.get(pk=pk)
        paso = int(request.data.get('paso', exp.paso_actual))
        datos = request.data.get('datos', request.data)
        WorkflowEngine.guardar_paso(exp, paso, datos, request.user)
        return Response(exp.to_dict())
    except Expediente.DoesNotExist:
        return Response({'detail': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except WorkflowError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def bandeja_api(request):
    tareas = WorkflowEngine.bandeja(request.user if request.user.is_authenticated else None)
    return Response({
        'total': tareas.count(),
        'tareas': [
            {
                'id': t.pk,
                'titulo': t.titulo,
                'expediente_id': t.expediente_id,
                'expediente_folio': t.expediente.folio,
                'paso': t.paso,
                'urgente': t.urgente,
                'vencimiento': t.vencimiento.isoformat() if t.vencimiento else None,
            }
            for t in tareas[:30]
        ],
    })
