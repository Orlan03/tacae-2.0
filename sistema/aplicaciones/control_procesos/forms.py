from django import forms
from .models import Proceso, Respuesta, CuentaPorCobrar, CXC

class ProcesoForm(forms.ModelForm):
    class Meta:
        model = Proceso
        fields = [
            'sorteo',
            'proceso',
            'responsable',
            'calificacion',
            'actor',
            'demandado',
            'valor',
            'posesion',
            'fecha_cumplimiento',
            'fecha_limite',
            'observaciones'
        ]
        widgets = {
            'fecha_cumplimiento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_limite': forms.DateInput(attrs={'type': 'date'}),
            'sorteo': forms.DateInput(attrs={'type': 'date'}),
        }
        
        


class RespuestaForm(forms.ModelForm):
    fecha_respuesta = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    fecha_cumplimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    class Meta:
        model = Respuesta
        fields = [
            'proceso',
            'fecha_respuesta',
            'calificacion',
            'fecha_cumplimiento',
            'observaciones'
        ]
        
        



class CuentaPorCobrarForm(forms.ModelForm):
    class Meta:
        model = CuentaPorCobrar
        fields = ["proceso", "cobro", "observacion"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cobro"].widget.attrs.update({
            "class": "form-control bg-dark text-white border-success",
            "placeholder": "Ingrese el monto cobrado"
        })
        self.fields["observacion"].widget.attrs.update({
            "class": "form-control bg-dark text-white border-info",
            "placeholder": "Ingrese una observación"
        })


class CXCForm(forms.ModelForm):
    class Meta:
        model = CXC
        fields = ['cliente', 'numero_factura', 'fecha', 'real', 'observacion']
        labels = {
            'cliente': 'Cliente',
            'numero_factura': '# Factura',
            'fecha': 'Fecha',
            'real': 'Real',
            'observacion': 'Observación'
        }
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'})
        }
