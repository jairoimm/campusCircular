from django.shortcuts import render
from rest_framework              import status
from rest_framework.decorators   import api_view, permission_classes
from rest_framework.permissions  import IsAuthenticated, AllowAny
from rest_framework.response     import Response
from django.shortcuts            import get_object_or_404
from django.utils                import timezone
from datetime                    import timedelta
from .models                     import Contenedor, RegistroResiduo
from .serializers                import ContenedorSerializer, RegistroResiduoSerializer
from puntos.models               import PerfilPuntos

# Create your views here.

# ── Tabla de puntos por tipo de residuo ───────────────────────────────────────
# Esta es la lógica central del sistema de gamificación
PUNTOS_POR_TIPO = {
    'organico'  : 10,
    'compost'   : 15,   # La compostera de gastronomía da más puntos
    'inorganico': 8,
    'papel'     : 8,
    'mixto'     : 5,
}


@api_view(['GET'])
@permission_classes([AllowAny])
def contenedor_por_qr(request, codigo_qr):
    """
    GET /api/residuos/contenedor/<codigo_qr>/
    Cuando el estudiante escanea el QR, React llama este endpoint.
    Devuelve los datos del contenedor para mostrar en la app.

    Si el QR no existe, devuelve 404.
    """
    contenedor = get_object_or_404(Contenedor, codigo_qr=codigo_qr, activo=True)
    serializer = ContenedorSerializer(contenedor)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_deposito(request):
    """
    POST /api/residuos/registrar/
    El endpoint más importante del sistema.
    Recibe el depósito del estudiante, calcula los puntos y los suma al perfil.

    Ejemplo de request:
    {
        "contenedor": 1,
        "peso_kg": 0.5,
        "observacion": ""
    }

    Ejemplo de respuesta:
    {
        "registro": { ... },
        "puntos_ganados": 10,
        "bonus_racha": 25,
        "puntos_totales": 250,
        "nivel": "brote",
        "mensaje": "¡Depósito registrado! Ganaste 10 puntos"
    }
    """
    serializer = RegistroResiduoSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    contenedor = get_object_or_404(
        Contenedor,
        id=request.data.get('contenedor'),
        activo=True
    )

    # ── Calcular puntos base según tipo de residuo del contenedor ─────────────
    puntos_base = PUNTOS_POR_TIPO.get(contenedor.tipo_residuo, 5)

    # ── Crear el registro ─────────────────────────────────────────────────────
    registro = serializer.save(
        usuario       = request.user,
        puntos_ganados = puntos_base
    )

    # ── Actualizar perfil de puntos ───────────────────────────────────────────
    perfil, _ = PerfilPuntos.objects.get_or_create(usuario=request.user)

    # Verificar y actualizar racha
    bonus_racha = 0
    hoy         = timezone.now().date()

    if perfil.ultimo_deposito:
        diferencia = (hoy - perfil.ultimo_deposito).days
        if diferencia == 0:
            # Ya depositó hoy, no suma racha
            pass
        elif diferencia == 1:
            # Depositó ayer → racha continúa
            perfil.racha_dias += 1
            # Si completa 5 días seguidos → bonus
            if perfil.racha_dias % 5 == 0:
                bonus_racha = 25
        else:
            # Rompió la racha
            perfil.racha_dias = 1
    else:
        # Primer depósito
        perfil.racha_dias = 1

    # Guardar mejor racha histórica
    if perfil.racha_dias > perfil.mejor_racha:
        perfil.mejor_racha = perfil.racha_dias

    perfil.ultimo_deposito = hoy

    # Sumar puntos base + bonus de racha
    total_puntos = puntos_base + bonus_racha
    perfil.sumar_puntos(total_puntos)   # Este método actualiza nivel automáticamente

    return Response({
        'registro'      : RegistroResiduoSerializer(registro).data,
        'puntos_ganados': puntos_base,
        'bonus_racha'   : bonus_racha,
        'puntos_totales': perfil.puntos_totales,
        'nivel'         : perfil.nivel_actual,
        'nivel_display' : perfil.get_nivel_actual_display(),
        'racha_dias'    : perfil.racha_dias,
        'mensaje'       : f'¡Depósito registrado! Ganaste {total_puntos} puntos 🌱',
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_registros(request):
    """
    GET /api/residuos/mis-registros/
    Devuelve el historial de depósitos del estudiante autenticado.
    React lo muestra en la sección "Mi historial" del perfil.
    """
    registros = RegistroResiduo.objects.filter(
        usuario=request.user
    ).select_related('contenedor').order_by('-fecha_hora')[:50]

    serializer = RegistroResiduoSerializer(registros, many=True)
    return Response(serializer.data)