import uuid
from usuarios.models import Usuario
from residuos.models import Contenedor
from puntos.models import Beneficio, PerfilPuntos

# ── Crear coordinadora ──────────────────────────────────────────────────────
if not Usuario.objects.filter(rut='11111111-1').exists():
    jazmin = Usuario.objects.create_user(
        rut='11111111-1',
        username='jazmin.jerez',
        password='inacap2025',
        first_name='Jazmín',
        last_name='Jerez',
        email='jazmin.jerez@inacap.cl',
        rol=Usuario.ROL_COORDINADOR,
        carrera='Docente Turismo'
    )
    print(f"✅ Coordinador creado: {jazmin}")

# ── Crear estudiante de prueba ──────────────────────────────────────────────
if not Usuario.objects.filter(rut='12345678-9').exists():
    estudiante = Usuario.objects.create_user(
        rut='12345678-9',
        username='sebastian.castro',
        password='inacap2025',
        first_name='Sebastián',
        last_name='Castro',
        email='sebastian.castro@inacapmail.cl',
        rol=Usuario.ROL_ESTUDIANTE,
        carrera='Informática',
        anio_cursando=2
    )
    PerfilPuntos.objects.create(usuario=estudiante, puntos_totales=240, puntos_disponibles=240)
    print(f"✅ Estudiante creado: {estudiante}")

# ── Crear contenedores ──────────────────────────────────────────────────────
contenedores = [
    ('Contenedor orgánico casino',      Contenedor.AREA_CASINO,      Contenedor.TIPO_ORGANICO,   80),
    ('Compostera gastronomía',          Contenedor.AREA_GASTRONOMICA, Contenedor.TIPO_COMPOST,    120),
    ('Punto verde reciclables',         Contenedor.AREA_PUNTO_VERDE, Contenedor.TIPO_INORGANICO, 100),
    ('Contenedor general área salud',   Contenedor.AREA_SALUD,       Contenedor.TIPO_MIXTO,      80),
    ('Contenedor locales comida',       Contenedor.AREA_LOCALES,     Contenedor.TIPO_ORGANICO,   80),
]

for nombre, area, tipo, altura in contenedores:
    if not Contenedor.objects.filter(nombre=nombre).exists():
        c = Contenedor.objects.create(
            nombre=nombre,
            area=area,
            tipo_residuo=tipo,
            codigo_qr=uuid.uuid4(),
            altura_cm=altura
        )
        print(f"✅ Contenedor creado: {c}")

# ── Crear beneficios ────────────────────────────────────────────────────────
beneficios = [
    ('Certificado digital de participación', 'Emitido por coordinación de sustentabilidad. Descargable como PDF.', 'reconocimiento', 200, 'Jazmín Jerez – Coordinación de Sustentabilidad', 'semilla'),
    ('Badge Guardián ♻️ en pantalla pública', 'Tu nombre aparece en la pantalla del hall del campus durante el mes.', 'reconocimiento', 600, 'Coordinación de Sustentabilidad', 'guardian'),
    ('Reserva prioritaria sala de estudio', 'Reserva con 48 hrs de anticipación vs 24 hrs normal.', 'academico', 150, 'Biblioteca / Recursos del campus', 'semilla'),
    ('Préstamo extendido de materiales', 'Plazo extendido de 3 a 7 días sin costo adicional.', 'academico', 250, 'Biblioteca / Bodega de talleres', 'brote'),
    ('Bolsa de compost del invernadero', 'Compost producido por las composteras del campus.', 'circular', 100, 'Talleres de Gastronomía', 'semilla'),
    ('Plantín del invernadero', 'Planta cultivada con el compost de las composteras.', 'circular', 180, 'Invernadero – Talleres de Gastronomía', 'semilla'),
    ('Título Embajador/a de Sustentabilidad', 'Nombramiento oficial por la dirección del campus.', 'comunidad', 400, 'Dirección del campus INACAP Puente Alto', 'arbol'),
]

for nombre, desc, cat, pts, gestor, nivel in beneficios:
    if not Beneficio.objects.filter(nombre=nombre).exists():
        b = Beneficio.objects.create(
            nombre=nombre,
            descripcion=desc,
            categoria=cat,
            costo_puntos=pts,
            gestor=gestor,
            nivel_minimo=nivel
        )
        print(f"✅ Beneficio creado: {b}")

print("\n🎉 Base de datos lista con datos de prueba")