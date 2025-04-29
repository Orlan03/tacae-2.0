# aplicaciones/control_procesos/context_processors.py

from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Proceso, Notificacion, Respuesta
from aplicaciones.eventos.models import Evento  # ajusta al path correcto

def notificaciones_unificadas_context_processor(request):
    """
    1) Eventos (tipo='evento') 5h antes de fecha_evento
    2) Procesos  (tipo='limite')  2d antes de fecha_limite
    3) Respuestas(tipo='respuesta') 2d antes de fecha_cumplimiento
    Devuelve `notificaciones_no_leidas` (combinadas y ordenadas) y `total_no_leidas`.
    """
    notis = []

    if request.user.is_authenticated:
        ahora = timezone.now()

        # ----- 1) Eventos (5h antes) -----
        corte_ev = ahora + timedelta(hours=5)
        eventos_prox = Evento.objects.filter(
            usuario=request.user,
            fecha_evento__gte=ahora,
            fecha_evento__lte=corte_ev
        )
        for ev in eventos_prox:
            if not Notificacion.objects.filter(
                usuario=request.user,
                tipo='evento',
                mensaje__icontains=ev.titulo
            ).exists():
                Notificacion.objects.create(
                    usuario=request.user,
                    tipo='evento',
                    mensaje=f"El evento “{ev.titulo}” es en menos de 5 horas.",
                    leida=False
                )

        # ----- 2) Procesos (2d antes) -----
        hoy = ahora.date()
        corte_pr = hoy + timedelta(days=2)
        procesos_prox = Proceso.objects.filter(
            fecha_limite__gte=hoy,
            fecha_limite__lte=corte_pr
        )
        for proc in procesos_prox:
            for usr in User.objects.all():
                if not Notificacion.objects.filter(
                    usuario=usr,
                    proceso=proc,
                    tipo='limite'
                ).exists():
                    Notificacion.objects.create(
                        usuario=usr,
                        proceso=proc,
                        tipo='limite',
                        mensaje=f"El proceso “{proc.proceso}” vence en menos de 2 días.",
                        leida=False
                    )

        # ----- 3) Respuestas (2d antes) -----
        respuestas_prox = Respuesta.objects.filter(
            fecha_cumplimiento__gte=hoy,
            fecha_cumplimiento__lte=corte_pr
        )
        for resp in respuestas_prox:
            for usr in User.objects.all():
                if not Notificacion.objects.filter(
                    usuario=usr,
                    proceso=resp.proceso,
                    tipo='respuesta'
                ).exists():
                    Notificacion.objects.create(
                        usuario=usr,
                        proceso=resp.proceso,
                        tipo='respuesta',
                        mensaje=(
                            f"La respuesta del proceso “{resp.proceso.proceso}” "
                            f"vence en menos de 2 días."
                        ),
                        leida=False
                    )

        # ----- Recuperar todas las no leídas y ordenarlas -----
        ev_no = Notificacion.objects.filter(usuario=request.user, tipo='evento',     leida=False)
        pr_no = Notificacion.objects.filter(usuario=request.user, tipo='limite',     leida=False)
        re_no = Notificacion.objects.filter(usuario=request.user, tipo='respuesta',  leida=False)

        notis = sorted(
            list(ev_no) + list(pr_no) + list(re_no),
            key=lambda n: n.fecha_creacion,
            reverse=True
        )

    total = len(notis)
    return {
        'notificaciones_no_leidas': notis,
        'total_no_leidas': total,
    }
