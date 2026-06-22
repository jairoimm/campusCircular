from rest_framework import serializers
from .models import Usuario
from puntos.models import PerfilPuntos

class PerfilPuntosSerializer(serializers.ModelSerializer):
    """serializer convierte objetos Python a JSON y viceversa."""

    nivel_display = serializers.CharField(
        source='get_nivel_actual_display',
        read_only=True
    )

    class Meta:
        model  = PerfilPuntos
        fields = [
            'puntos_totales',
            'puntos_disponibles',
            'nivel_actual',
            'nivel_display',
            'racha_dias',
            'mejor_racha',
            'ultimo_deposito',
        ]


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer del usuario. Incluye su perfil de puntos anidado.
    """
    perfil_puntos  = PerfilPuntosSerializer(read_only=True)
    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        model  = Usuario
        fields = [
            'id',
            'rut',
            'nombre_completo',
            'first_name',
            'last_name',
            'email',
            'carrera',
            'anio_cursando',
            'rol',
            'fecha_registro',
            'perfil_puntos',
        ]
        # El password nunca viaja en la respuesta
        read_only_fields = ['id', 'fecha_registro', 'rol']


class LoginSerializer(serializers.Serializer):
    """
    Serializer para el login. Solo recibe RUT y password.
    """
    rut      = serializers.CharField(max_length=12)
    password = serializers.CharField(write_only=True)