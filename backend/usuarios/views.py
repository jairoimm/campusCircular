from django.shortcuts import render
from rest_framework              import status
from rest_framework.decorators   import api_view, permission_classes
from rest_framework.permissions  import AllowAny, IsAuthenticated
from rest_framework.response     import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth         import authenticate
from .models       import Usuario
from .serializers  import UsuarioSerializer, LoginSerializer

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])   # Este endpoint NO requiere login
def login_view(request):
    """
    POST /api/auth/login/
    El estudiante envía su RUT y password.
    Django verifica y devuelve un TOKEN.
    React guarda ese token y lo manda en cada request siguiente.

    Ejemplo de request:
    { "rut": "12345678-9", "password": "inacap2025" }

    Ejemplo de respuesta exitosa:
    { "token": "abc123...", "usuario": { ... } }
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    rut      = serializer.validated_data['rut']
    password = serializer.validated_data['password']

    # authenticate busca el usuario con ese RUT y verifica el password
    usuario = authenticate(request, username=rut, password=password)

    if usuario is None:
        return Response(
            {'error': 'RUT o contraseña incorrectos'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # get_or_create devuelve el token existente o crea uno nuevo
    token, _ = Token.objects.get_or_create(user=usuario)

    return Response({
        'token'  : token.key,
        'usuario': UsuarioSerializer(usuario).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    POST /api/auth/logout/
    Elimina el token del usuario, cerrando su sesión.
    """
    request.user.auth_token.delete()
    return Response({'mensaje': 'Sesión cerrada correctamente'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def perfil_view(request):
    """
    GET /api/auth/perfil/
    Devuelve los datos del usuario actualmente autenticado.
    React usa esto para mostrar el nombre, puntos y nivel en la app.
    """
    serializer = UsuarioSerializer(request.user)
    return Response(serializer.data)