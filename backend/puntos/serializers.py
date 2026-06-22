from rest_framework import serializers
from .models        import PerfilPuntos, Beneficio, Canje

class BeneficioSerializer(serializers.ModelSerializer):
    categoria_display  = serializers.CharField(source='get_categoria_display',  read_only=True)
    nivel_minimo_display = serializers.CharField(source='get_nivel_minimo_display', read_only=True)

    class Meta:
        model  = Beneficio
        fields = [
            'id', 'nombre', 'descripcion',
            'categoria', 'categoria_display',
            'costo_puntos', 'gestor', 'activo',
            'nivel_minimo', 'nivel_minimo_display',
        ]


class CanjeSerializer(serializers.ModelSerializer):
    beneficio_nombre = serializers.CharField(source='beneficio.nombre', read_only=True)
    estado_display   = serializers.CharField(source='get_estado_display', read_only=True)
    usuario_nombre   = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    usuario_carrera  = serializers.CharField(source='usuario.carrera', read_only=True)

    class Meta:
        model  = Canje
        fields = [
            'id', 'usuario', 'usuario_nombre', 'usuario_carrera',
            'beneficio', 'beneficio_nombre',
            'estado', 'estado_display',
            'puntos_descontados', 'codigo_canje',
            'fecha_solicitud', 'fecha_aprobacion', 'fecha_entrega',
        ]
        read_only_fields = [
            'id', 'usuario', 'puntos_descontados',
            'codigo_canje', 'fecha_solicitud',
            'fecha_aprobacion', 'fecha_entrega',
        ]