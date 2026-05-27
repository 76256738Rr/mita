"""Formularios de la plataforma MITA."""

from django import forms


class ExpedienteNuevoForm(forms.Form):
    titulo = forms.CharField(max_length=300, label='Título de la iniciativa')
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, label='Descripción')
    solicitante = forms.CharField(max_length=200, required=False, label='Solicitante')
    dependencia = forms.CharField(max_length=200, required=False, label='Dependencia')


class Paso1Form(forms.Form):
    titulo = forms.CharField(max_length=300)
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)
    solicitante = forms.CharField(max_length=200, required=False)
    dependencia = forms.CharField(max_length=200, required=False)


class Paso4Form(forms.Form):
    marco_legal = forms.BooleanField(required=False)
    derechos_humanos = forms.BooleanField(required=False)
    normativa_aplicable = forms.BooleanField(required=False)
    recursos_tecnicos = forms.BooleanField(required=False)
    infraestructura = forms.BooleanField(required=False)
    plazo_ejecucion = forms.BooleanField(required=False)
    presupuesto = forms.FloatField(required=False, initial=0)
    retorno_inversion = forms.BooleanField(required=False)
    sostenibilidad = forms.BooleanField(required=False)
    beneficiarios = forms.BooleanField(required=False)
    necesidad_identificada = forms.BooleanField(required=False)
    impacto_esperado = forms.BooleanField(required=False)
    enfoque_integral = forms.BooleanField(required=False)
    adaptacion_cultural = forms.BooleanField(required=False)
    interculturalidad = forms.BooleanField(required=False)
    ejes_accion = forms.MultipleChoiceField(
        choices=[(str(i), f'Eje {i}') for i in range(1, 7)],
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def to_criterios(self, expediente):
        data = self.cleaned_data
        return {
            'titulo': expediente.titulo,
            'descripcion': expediente.descripcion,
            'solicitante': expediente.solicitante,
            **data,
            'ejes_accion': [int(x) for x in data.get('ejes_accion', [])],
        }


class Paso6Form(forms.Form):
    opcion_id = forms.IntegerField(widget=forms.RadioSelect, label='Opción seleccionada')

    def __init__(self, *args, opciones=None, **kwargs):
        super().__init__(*args, **kwargs)
        if opciones:
            self.fields['opcion_id'].widget = forms.RadioSelect(
                choices=[(o.pk, f'{o.titulo} ({o.puntuacion:.0f} pts)') for o in opciones],
            )


class ComentarioAvanceForm(forms.Form):
    comentario = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False, label='Comentario')
