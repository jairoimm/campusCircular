from django.shortcuts import render
import uuid
from rest_framework              import status
from rest_framework.decorators   import api_view, permission_classes
from rest_framework.permissions  import IsAuthenticated
from rest_framework.response     import Response
from django.shortcuts            import get_object_or_404
from django.utils                import timezone
from django.db.models            import Sum, Count
from .models                     import PerfilPuntos, Beneficio, Canje
from .serializers                import BeneficioSerializer, CanjeSerializer
from usuarios.models             import Usuario
from residuos.models             import RegistroResiduo

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_puntos(request):
    """
    GET /api/puntos/mis-puntos/
    Devuelve el perfil de puntos completo del estudiante.
    """
    perfil, _ = PerfilPuntos.objects.get_or_create(usuario=request.user)
    return Response({
        'puntos_totales'    : perfil.puntos_totales,
        'puntos_disponibles': perfil.puntos_disponibles,
        'nivel'             : perfil.nivel_actual,
        'nivel_display'     : perfil.get_nivel_actual_display(),
        'racha_dias'        : perfil.racha_dias,
        'mejor_racha'       : perfil.mejor_racha,
        'proximo_nivel'     : _proximo_nivel(perfil),
    })


def _proximo_nivel(perfil):
    """Calcula cuántos puntos faltan para el siguiente nivel"""
    umbrales = {'semilla': 100, 'brote': 300, 'arbol': 600}
    siguiente_pts = umbrales.get(perfil.nivel_actual)
    if siguiente_pts:
        return {
            'puntos_necesarios': siguiente_pts,
            'puntos_faltan'    : max(0, siguiente_pts - perfil.puntos_totales),
        }
    return None  # Ya es Guardián, nivel máximo


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lista_beneficios(request):
    """
    GET /api/puntos/beneficios/
    Lista todos los beneficios activos.
    Para cada uno indica si el estudiante puede canjearlo.
    """
    perfil, _  = PerfilPuntos.objects.get_or_create(usuario=request.user)
    beneficios = Beneficio.objects.filter(activo=True)
    serializer = BeneficioSerializer(beneficios, many=True)

    # Agregar campo "puede_canjear" a cada beneficio
    data = serializer.data
    for item in data:
        item['puede_canjear'] = (
            perfil.puntos_disponibles >= item['costo_puntos']
        )
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def solicitar_canje(request):
    """
    POST /api/puntos/canjear/
    El estudiante solicita un beneficio.

    Ejemplo de request:
    { "beneficio_id": 1 }

    Django verifica que tenga puntos suficientes,
    descuenta los puntos y crea el canje en estado PENDIENTE.
    Jazmín lo aprueba desde su panel.
    """
    beneficio_id = request.data.get('beneficio_id')
    if not beneficio_id:
        return Response({'error': 'beneficio_id es requerido'}, status=400)

    beneficio = get_object_or_404(Beneficio, id=beneficio_id, activo=True)
    perfil, _ = PerfilPuntos.objects.get_or_create(usuario=request.user)

    # Verificar que tiene puntos suficientes
    if perfil.puntos_disponibles < beneficio.costo_puntos:
        return Response(
            {'error': f'Puntos insuficientes. Necesitas {beneficio.costo_puntos} pts, tienes {perfil.puntos_disponibles} pts'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Descontar los puntos
    perfil.puntos_disponibles -= beneficio.costo_puntos
    perfil.save()

    # Crear el canje en estado PENDIENTE
    canje = Canje.objects.create(
        usuario            = request.user,
        beneficio          = beneficio,
        puntos_descontados = beneficio.costo_puntos,
        estado             = Canje.ESTADO_PENDIENTE,
    )

    return Response({
        'canje'             : CanjeSerializer(canje).data,
        'puntos_disponibles': perfil.puntos_disponibles,
        'mensaje'           : f'Solicitud enviada. Jazmín aprobará tu {beneficio.nombre} pronto 🎁',
    }, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def aprobar_canje(request, canje_id):
    """
    PATCH /api/puntos/canje/<id>/aprobar/
    Solo la coordinadora puede aprobar canjes.
    Genera el QR de canje para que el estudiante lo presente.
    """
    if not request.user.es_coordinadora:
        return Response({'error': 'Solo la coordinadora puede aprobar canjes'}, status=403)

    canje = get_object_or_404(Canje, id=canje_id, estado=Canje.ESTADO_PENDIENTE)
    canje.estado          = Canje.ESTADO_APROBADO
    canje.codigo_canje    = uuid.uuid4()  # Genera QR único para el estudiante
    canje.fecha_aprobacion = timezone.now()
    canje.save()

    return Response({
        'canje'  : CanjeSerializer(canje).data,
        'mensaje': f'Canje aprobado. El estudiante recibirá su QR en la app.',
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    """
    GET /api/puntos/dashboard/
    Datos completos para el dashboard de Jazmín y la pantalla pública.
    Este endpoint reúne todas las métricas en una sola llamada.
    """
    from django.db.models.functions import TruncWeek
    from datetime                   import date, timedelta

    hoy        = date.today()
    inicio_mes = hoy.replace(day=1)

    # ── Métricas generales del mes ────────────────────────────────────────────
    registros_mes = RegistroResiduo.objects.filter(fecha_hora__date__gte=inicio_mes)

    total_kg      = registros_mes.aggregate(total=Sum('peso_kg'))['total'] or 0
    total_depositos = registros_mes.count()
    estudiantes_activos = registros_mes.values('usuario').distinct().count()
    canjes_pendientes   = Canje.objects.filter(estado=Canje.ESTADO_PENDIENTE).count()

    # CO2 evitado: estimación simple — 1 kg reciclado ≈ 0.26 kg CO2
    co2_evitado = round(float(total_kg) * 0.26, 1)

    # ── Ranking de carreras ───────────────────────────────────────────────────
    ranking = (
        PerfilPuntos.objects
        .values('usuario__carrera')
        .annotate(total_pts=Sum('puntos_totales'))
        .order_by('-total_pts')[:5]
    )

    # ── Guardianes del mes (nivel guardian) ───────────────────────────────────
    guardianes = (
        PerfilPuntos.objects
        .filter(nivel_actual='guardian')
        .select_related('usuario')
        .order_by('-puntos_totales')[:3]
    )

    guardianes_data = [{
        'nombre' : g.usuario.nombre_completo,
        'carrera': g.usuario.carrera,
        'puntos' : g.puntos_totales,
    } for g in guardianes]

    # ── Registros por semana (para el gráfico) ────────────────────────────────
    por_semana = (
        RegistroResiduo.objects
        .filter(fecha_hora__date__gte=inicio_mes)
        .annotate(semana=TruncWeek('fecha_hora'))
        .values('semana')
        .annotate(total_kg=Sum('peso_kg'), depositos=Count('id'))
        .order_by('semana')
    )

    return Response({
        'metricas': {
            'total_kg'           : float(total_kg),
            'co2_evitado_kg'     : co2_evitado,
            'estudiantes_activos': estudiantes_activos,
            'total_depositos'    : total_depositos,
            'canjes_pendientes'  : canjes_pendientes,
        },
        'ranking_carreras': list(ranking),
        'guardianes'      : guardianes_data,
        'por_semana'      : list(por_semana),
    })