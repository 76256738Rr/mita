from django.contrib import admin
from django.urls import include, path

from core.auth_views import MitaLoginView
from core.views import (
    MitaLogoutView,
    analogia_view,
    base_datos_view,
    dashboard_view,
    dictamenes_view,
    mapa_view,
    metodologia_view,
    proceso_view,
    proyecto_view,
    reportes_view,
    sni_view,
)
from core.ciudadania_views import (
    asistente_ia_api,
    campos_eje_api,
    centros_salud_api,
    portal_ciudadano_view,
    reporte_chat_api,
    reporte_detalle_view,
    reporte_nuevo_view,
    ubicaciones_eje_api,
)
from core.workflow_views import (
    bandeja_view,
    expediente_detalle_view,
    expediente_nuevo_view,
    expedientes_list_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', dashboard_view, name='dashboard'),
    path('bandeja/', bandeja_view, name='bandeja'),
    path('expedientes/', expedientes_list_view, name='expedientes'),
    path('expedientes/nuevo/', expediente_nuevo_view, name='expediente-nuevo'),
    path('expedientes/<int:pk>/', expediente_detalle_view, name='expediente-detalle'),
    path('ciudadania/', portal_ciudadano_view, name='ciudadania-portal'),
    path('ciudadania/nuevo/', reporte_nuevo_view, name='ciudadania-nuevo'),
    path('ciudadania/reporte/<int:pk>/', reporte_detalle_view, name='ciudadania-detalle'),
    path('ciudadania/api/asistente/', asistente_ia_api, name='ciudadania-asistente'),
    path('ciudadania/api/eje/<str:eje_slug>/campos/', campos_eje_api, name='ciudadania-campos-eje'),
    path('ciudadania/api/centros-salud/', centros_salud_api, name='ciudadania-centros-salud'),
    path('ciudadania/api/eje/<str:eje_slug>/ubicaciones/', ubicaciones_eje_api, name='ciudadania-ubicaciones'),
    path('ciudadania/api/reporte/<int:pk>/chat/', reporte_chat_api, name='ciudadania-chat'),
    path('base-datos/', base_datos_view, name='base-datos'),
    path('mapa/', mapa_view, name='mapa'),
    path('metodologia/', metodologia_view, name='metodologia'),
    path('proceso/', proceso_view, name='proceso'),
    path('proyecto/', proyecto_view, name='proyecto'),
    path('analogia/', analogia_view, name='analogia'),
    path('sni/', sni_view, name='sni'),
    path('reportes/', reportes_view, name='reportes'),
    path('dictamenes/', dictamenes_view, name='dictamenes'),
    path('login/', MitaLoginView.as_view(), name='login'),
    path('logout/', MitaLogoutView.as_view(), name='logout'),
]
