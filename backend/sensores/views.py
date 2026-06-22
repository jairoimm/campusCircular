from django.shortcuts import render
from rest_framework              import status
from rest_framework.decorators   import api_view, permission_classes
from rest_framework.permissions  import AllowAny, IsAuthenticated
from rest_framework.response     import Response
from django.shortcuts            import get_object_or_404
from .models                     import LecturaSensor, AlertaContenedor
from .serializers                import LecturaSensorSerializer, AlertaContenedorSerializer
from residuos.models             import Contenedor

# Create your views here.

# Token válido para los ESP32 del campus (en producción iría en .env)
TOKEN_ESP32_VALIDO = 'campuscircular-esp32-inacap-2025'


@api_view(['POST'])
@permission_classes([AllowAny])
def recibir_lectura(request):
    """
    POST /api/sensores/lectura/
    El ESP32 llama este endpoint cada 10 minutos con la lectura del sensor.

    Ejemplo de payload que envía el ESP32:
    {
        "contenedor_id": 1,
        "distancia_cm": 23.5,
        "token": "campuscircular-esp32-inacap-2025"
    }

    Django calcula el porcentaje, guarda la lectura
    y genera alertas automáticas si supera el 80% o 95%.
    """
    # Verificar que el token del ESP32 es válido
    token = request.data.get('token')
    if token != TOKEN_ESP32_VALIDO:
        return Response(
            {'error': 'Token de dispositivo inválido'},
            status=status.HTTP_403_FORBIDDEN
        )

    contenedor_id = request.data.get('contenedor_id')
    distancia_cm  = request.data.get('distancia_cm')

    if not contenedor_id or distancia_cm is None:
        return Response(
            {'error': 'Faltan campos: contenedor_id y distancia_cm'},
            status=status.HTTP_400_BAD_REQUEST
        )

    contenedor = get_object_or_404(Contenedor, id=contenedor_id, activo=True)

    # ── Calcular porcentaje de llenado ────────────────────────────────────────
    # Fórmula: (altura_total - distancia_medida) / altura_total * 100
    # Ejemplo: contenedor de 80cm, sensor lee 20cm de distancia
    # → (80 - 20) / 80 * 100 = 75% lleno
    distancia_cm       = float(distancia_cm)
    porcentaje_llenado = ((contenedor.altura_cm - distancia_cm) / contenedor.altura_cm) * 100
    porcentaje_llenado = max(0, min(100, round(porcentaje_llenado, 1)))  # Clamp entre 0 y 100

    # ── Guardar la lectura ────────────────────────────────────────────────────
    lectura = LecturaSensor.objects.create(
        contenedor         = contenedor,
        distancia_cm       = distancia_cm,
        porcentaje_llenado = porcentaje_llenado,
        token_dispositivo  = token,
    )

    # ── Generar alertas automáticas ───────────────────────────────────────────
    alerta_generada = None

    if porcentaje_llenado >= 95:
        # Alerta URGENTE — notificar a Jazmín y a la municipalidad si es punto verde
        alerta, creada = AlertaContenedor.objects.get_or_create(
            contenedor = contenedor,
            nivel      = AlertaContenedor.NIVEL_URGENTE,
            atendida   = False,
            defaults   = {
                'porcentaje_al_momento'   : porcentaje_llenado,
                'notificado_municipalidad': contenedor.area == Contenedor.AREA_PUNTO_VERDE,
            }
        )
        if creada:
            alerta_generada = 'urgente'

    elif porcentaje_llenado >= 80:
        # Alerta de AVISO
        alerta, creada = AlertaContenedor.objects.get_or_create(
            contenedor = contenedor,
            nivel      = AlertaContenedor.NIVEL_AVISO,
            atendida   = False,
            defaults   = {'porcentaje_al_momento': porcentaje_llenado}
        )
        if creada:
            alerta_generada = 'aviso'

    return Response({
        'lectura_id'        : lectura.id,
        'contenedor'        : contenedor.nombre,
        'porcentaje_llenado': porcentaje_llenado,
        'estado'            : lectura.estado,
        'alerta_generada'   : alerta_generada,
        'mensaje'           : f'Lectura registrada: {porcentaje_llenado}% lleno',
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estado_contenedores(request):
    """
    GET /api/sensores/estado/
    Devuelve la última lectura de cada contenedor.
    El dashboard de Jazmín y la pantalla pública llaman esto.
    """
    contenedores = Contenedor.objects.filter(activo=True)
    resultado    = []

    for contenedor in contenedores:
        # Obtenemos solo la última lectura de cada contenedor
        ultima = LecturaSensor.objects.filter(
            contenedor=contenedor
        ).order_by('-timestamp').first()

        resultado.append({
            'contenedor_id'    : contenedor.id,
            'nombre'           : contenedor.nombre,
            'area'             : contenedor.get_area_display(),
            'tipo_residuo'     : contenedor.get_tipo_residuo_display(),
            'porcentaje_llenado': float(ultima.porcentaje_llenado) if ultima else None,
            'estado'           : ultima.estado if ultima else 'sin_datos',
            'ultima_lectura'   : ultima.timestamp if ultima else None,
        })

    return Response(resultado)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alertas_activas(request):
    """
    GET /api/sensores/alertas/
    Devuelve todas las alertas no atendidas.
    Jazmín las ve en su panel y puede marcarlas como atendidas.
    """
    alertas    = AlertaContenedor.objects.filter(atendida=False).order_by('-fecha_creacion')
    serializer = AlertaContenedorSerializer(alertas, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def atender_alerta(request, alerta_id):
    """
    PATCH /api/sensores/alertas/<id>/atender/
    Jazmín marca una alerta como atendida desde su panel.
    """
    from django.utils import timezone
    alerta = get_object_or_404(AlertaContenedor, id=alerta_id)
    alerta.atendida     = True
    alerta.fecha_atencion = timezone.now()
    alerta.save()
    return Response({'mensaje': 'Alerta marcada como atendida'})