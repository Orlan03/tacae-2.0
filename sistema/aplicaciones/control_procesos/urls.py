from django.urls import path
from .views import registrar_proceso, listar_procesos, listar_carpetas, editar_proceso, eliminar_proceso, registrar_respuesta, listar_respuestas_subcarpeta, listar_respuestas_por_nombre, listar_cuentas_por_cobrar, registrar_cuenta_por_cobrar, crear_cxc_tacae, editar_cxc, eliminar_cxc

app_name = 'control_procesos'

urlpatterns = [
    
    path('listar/<int:carpeta_id>/', listar_procesos, name='listar_procesos'),
    path('registrar/<int:carpeta_id>/', registrar_proceso, name='registrar_proceso'),
    path('', listar_carpetas, name='listar_carpetas'),
    path("editar/<int:proceso_id>/", editar_proceso, name="editar_proceso"),
    path("eliminar/<int:proceso_id>/", eliminar_proceso, name="eliminar_proceso"),
    path('respuestas/registrar/<int:carpeta_id>/', registrar_respuesta, name='registrar_respuesta'),
    path('respuestas/subcarpeta/<int:carpeta_id>/', listar_respuestas_subcarpeta, name='listar_respuestas_subcarpeta'),
    path('respuestas/por_nombre/<int:carpeta_id>/', listar_respuestas_por_nombre, name='listar_respuestas_por_nombre'),
    path("cuentas/listar/<int:carpeta_id>/", listar_cuentas_por_cobrar, name="listar_cuentas_por_cobrar"),
    path('cuentas/registrar/<int:carpeta_id>/', registrar_cuenta_por_cobrar, name='registrar_cuenta_por_cobrar'),
    path('cxc/crear/<int:carpeta_id>/', crear_cxc_tacae, name='crear_cxc'),
    path('cxc/editar/<int:cxc_id>/', editar_cxc, name='editar_cxc'),
    path('cxc/eliminar/<int:cxc_id>/', eliminar_cxc, name='eliminar_cxc'),
    
]
