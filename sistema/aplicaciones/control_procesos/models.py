from django.db import models
from aplicaciones.carpetas.models import Carpeta
from django.contrib.auth.models import User

class Proceso(models.Model):
    sorteo = models.DateField(blank=True, null=True)
    proceso = models.CharField(max_length=200)
    responsable = models.CharField(max_length=200, default="Desconocido")
    calificacion = models.CharField(max_length=100, blank=True, null=True)
    actor = models.CharField(max_length=200, default="Desconocido")
    demandado = models.CharField(max_length=200, default="Desconocido")
    valor = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    posesion = models.CharField(max_length=100, blank=True, null=True)
    fecha_cumplimiento = models.DateField(blank=True, null=True)
    fecha_limite = models.DateField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    carpeta = models.ForeignKey(Carpeta, on_delete=models.CASCADE, related_name='procesos')

    def __str__(self):
        return self.proceso
    
    



class Respuesta(models.Model):
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE, related_name="respuestas")
    carpeta = models.ForeignKey(Carpeta, on_delete=models.CASCADE, related_name="respuestas", null=True, blank=True)
    fecha_respuesta = models.DateField()
    calificacion = models.CharField(max_length=100, blank=True, null=True)
    fecha_cumplimiento = models.DateField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Respuesta de {self.proceso} - {self.fecha_respuesta}"
    


class CuentaPorCobrar(models.Model):
    carpeta = models.ForeignKey(Carpeta, on_delete=models.CASCADE, related_name="cuentas_por_cobrar")
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE, related_name="cuentas_cobrar")
    cobro = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    observacion = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Asegura que el saldo siempre sea actualizado correctamente"""
        self.saldo = self.proceso.valor - self.cobro  # Restar cobro al valor total
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.proceso.proceso} - {self.cobro}"



class CXC(models.Model):
    carpeta = models.ForeignKey(
        Carpeta, 
        on_delete=models.CASCADE,
        related_name='cxcs',  # Para acceder a las CXC desde la carpeta usando carpeta.cxcs.all()
        null=True, 
        blank=True
    )
    cliente = models.CharField(max_length=255, blank=True, null=True)
    numero_factura = models.CharField(max_length=100, blank=True, null=True)
    fecha = models.CharField(max_length=255, blank=True, null=True)  # o DateField
    real = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.cliente or 'Sin Cliente'} - {self.numero_factura or 'Sin Factura'}"


class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notificaciones_control")
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE, null=True, blank=True)
    mensaje = models.CharField(max_length=255)
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # Opcionalmente, un campo para distinguir el tipo de notificación
    tipo = models.CharField(max_length=50, default="general")

    def __str__(self):
        return self.mensaje