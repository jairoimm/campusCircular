from rest_framework import serializers
from .models        import Contenedor, RegistroResiduo

class ContenedorSerializer(serializers.ModelSerializer):
    """Serializer del contenedor — incluye área y tipo en formato legible"""
    area_display         = serializers.CharField(source='get_area_display',        read_only=True)
    tipo_residuo_display = serializers.CharField(source='get_tipo_residuo_display', read_only=True)

    class Meta:
        model  = Contenedor
        fields = [
            'id', 'nombre', 'area', 'area_display',
            'tipo_residuo', 'tipo_residuo_display',
            'codigo_qr', 'altura_cm', 'activo',
        ]


class RegistroResiduoSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y listar registros de residuo.
    Cuando React manda el depósito, este serializer lo valida.
    """
    usuario_nombre   = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    contenedor_nombre = serializers.CharField(source='contenedor.nombre',       read_only=True)
    contenedor_area   = serializers.CharField(source='contenedor.get_area_display', read_only=True)

    class Meta:
        model  = RegistroResiduo
        fields = [
            'id', 'usuario', 'usuario_nombre',
            'contenedor', 'contenedor_nombre', 'contenedor_area',
            'peso_kg', 'peso_automatico',
            'fecha_hora', 'puntos_ganados', 'observacion',
        ]
        read_only_fields = ['id', 'fecha_hora', 'puntos_ganados', 'usuario']