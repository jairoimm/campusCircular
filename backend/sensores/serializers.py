from rest_framework import serializers
from .models        import LecturaSensor, AlertaContenedor

class LecturaSensorSerializer(serializers.ModelSerializer):
    estado            = serializers.CharField(read_only=True)
    contenedor_nombre = serializers.CharField(source='contenedor.nombre', read_only=True)
    contenedor_area   = serializers.CharField(source='contenedor.get_area_display', read_only=True)

    class Meta:
        model  = LecturaSensor
        fields = [
            'id', 'contenedor', 'contenedor_nombre', 'contenedor_area',
            'distancia_cm', 'porcentaje_llenado',
            'timestamp', 'token_dispositivo', 'estado',
        ]
        read_only_fields = ['id', 'timestamp', 'estado']


class AlertaContenedorSerializer(serializers.ModelSerializer):
    contenedor_nombre = serializers.CharField(source='contenedor.nombre', read_only=True)
    nivel_display     = serializers.CharField(source='get_nivel_display', read_only=True)

    class Meta:
        model  = AlertaContenedor
        fields = [
            'id', 'contenedor', 'contenedor_nombre',
            'nivel', 'nivel_display', 'porcentaje_al_momento',
            'atendida', 'fecha_creacion', 'notificado_municipalidad',
        ]