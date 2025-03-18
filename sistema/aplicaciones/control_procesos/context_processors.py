from datetime import timedelta
from django.utils import timezone
from .models import Proceso, Notificacion
from django.contrib.auth.models import User


def procesos_limite_context_processor(request):
    if request.user.is_authenticated:
        ahora = timezone.now().date()  # Asumiendo que fecha_limite es DateField
        # Obtén todos los procesos con fecha_limite en las próximas 24 horas (sin filtrar por usuario)
        procesos_pendientes = Proceso.objects.filter(
            fecha_limite__gte=ahora,
            fecha_limite__lte=ahora + timedelta(days=1)
        )
        # Para cada proceso pendiente, notifica a todos los usuarios
        for proceso in procesos_pendientes:
            for usuario in User.objects.all():
                # Verifica si ya existe una notificación para este proceso y usuario
                existe = Notificacion.objects.filter(
                    proceso=proceso,
                    usuario=usuario,
                    tipo="limite",
                    mensaje__icontains="fecha límite"
                ).exists()
                if not existe:
                    Notificacion.objects.create(
                        usuario=usuario,
                        proceso=proceso,
                        mensaje=f"El proceso '{proceso.proceso}' se acerca a su fecha límite.",
                        tipo="limite",
                        leida=False
                    )
        # Para devolver notificaciones no leídas del usuario actual, usamos el related_name correcto
        notis_no_leidas = request.user.notificaciones_control.filter(leida=False)
    else:
        notis_no_leidas = []
    return {'notificaciones_no_leidas': notis_no_leidas}


def notificaciones_unificadas_context_processor(request):
    if request.user.is_authenticated:
        total_eventos = request.user.notificaciones_eventos.filter(leida=False).count()
        total_control = request.user.notificaciones_control.filter(leida=False).count()
        total_no_leidas = total_eventos + total_control
    else:
        total_no_leidas = 0
    return {'total_no_leidas': total_no_leidas}