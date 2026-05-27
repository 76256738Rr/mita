from rest_framework import serializers


class PropuestaEvaluacionSerializer(serializers.Serializer):
    titulo = serializers.CharField(max_length=300)
    descripcion = serializers.CharField(required=False, allow_blank=True, default='')
    marco_legal = serializers.BooleanField(default=False)
    derechos_humanos = serializers.BooleanField(default=False)
    normativa_aplicable = serializers.BooleanField(default=False)
    recursos_tecnicos = serializers.BooleanField(default=False)
    infraestructura = serializers.BooleanField(default=False)
    plazo_ejecucion = serializers.BooleanField(default=False)
    presupuesto = serializers.FloatField(default=0)
    retorno_inversion = serializers.BooleanField(default=False)
    sostenibilidad = serializers.BooleanField(default=False)
    beneficiarios = serializers.BooleanField(default=False)
    necesidad_identificada = serializers.BooleanField(default=False)
    impacto_esperado = serializers.BooleanField(default=False)
    ejes_accion = serializers.ListField(child=serializers.IntegerField(), default=list)
    enfoque_integral = serializers.BooleanField(default=False)
    adaptacion_cultural = serializers.BooleanField(default=False)
    interculturalidad = serializers.BooleanField(default=False)
    solicitante = serializers.CharField(required=False, allow_blank=True, default='')


class CruceRequestSerializer(serializers.Serializer):
    disciplina_ids = serializers.ListField(child=serializers.CharField())
