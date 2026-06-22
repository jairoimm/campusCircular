from django.db import models
from django.conf import settings

# Create your models here.

class PerfilPuntos(models.Model):
    NIVEL_SEMILLA = 'semilla' #0-99 puntos
    NIVEL_BROTE = 'brote' #100-299 puntos
    NIVEL_ARBOL = 'arbol' #300-599 puntos
    NIVEL_GUARDIAN = 'guardian' #600+ puntos

    NIVEL_CHOICES = [
        (NIVEL_SEMILLA, '🌱 Semilla'),
        (NIVEL_BROTE, '🌿 Brote'),
        (NIVEL_ARBOL, '🌳 Árbol'),
        (NIVEL_GUARDIAN, '♻️Guardián'),
    ]

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil_puntos", verbose_name="Estudiante")
    puntos_totales = models.PositiveIntegerField(default=0, verbose_name="Puntos totales acumulados")
    puntos_disponibles = models.PositiveIntegerField(default=0, verbose_name="Puntos disponibles para canjear")
    nivel_actual = models.CharField(max_length=10, choices=NIVEL_CHOICES, default=NIVEL_SEMILLA, verbose_name="Nivel actual")
    racha_dias = models.PositiveSmallIntegerField(default=0, verbose_name="Racha de días consecutivos reciclando")
    mejor_racha = models.PositiveSmallIntegerField(default=0, verbose_name="Mejor racha registrada")
    ultimo_deposito = models.DateField(null=True, blank=True, verbose_name="Último dia de deposito")

    class Meta:
        verbose_name = "Perfil de Puntos"
        verbose_name_plural = "Perfiles de Puntos"
        
    def __str__(self):
        return f"{self.usuario.nombre_completo} - {self.puntos_totales} pts ({self.get_nivel_actual_display()})"
    
    def calcular_nivel(self):
        if self.puntos_totales >= 600:
            return self.NIVEL_GUARDIAN
        elif self.puntos_totales >= 300:
            return self.NIVEL_ARBOL
        elif self.puntos_totales >= 100:
            return self.NIVEL_BROTE
        else:
            return self.NIVEL_SEMILLA
    
    def sumar_puntos(self, cantidad):
        self.puntos_totales += cantidad
        self.puntos_disponibles += cantidad
        self.nivel_actual = self.calcular_nivel()
        self.save()

class Beneficio(models.Model):
    CATEGORIA_RECONOCIMIENTO = 'reconocimiento'
    CATEGORIA_ACADEMICO = 'academico'
    CATEGORIA_CIRCULAR = 'circular'
    CATEGORIA_COMUNIDAD = 'comunidad'

    CATEGORIA_CHOICES = [
        (CATEGORIA_RECONOCIMIENTO, '🏅 Reconocimiento institucional'),
        (CATEGORIA_ACADEMICO, '📚 Reconocimiento académico'),
        (CATEGORIA_CIRCULAR, '🌱 Economía circular'),
        (CATEGORIA_COMUNIDAD, '📣 Comunidad y visibilidad'),
    ]

    nombre = models.CharField(max_length=100, verbose_name="Nombre del beneficio")
    descripcion = models.TextField(verbose_name="Descripción del beneficio")
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    costo_puntos = models.PositiveSmallIntegerField(verbose_name="Costo en puntos")
    gestor = models.CharField(max_length=100, verbose_name='quien entrega el beneficio', help_text='ej: Coordinacion de Sustentabilidad, biblioteca')
    activo = models.BooleanField(default=True)
    nivel_minimo = models.CharField(max_length=10, choices=PerfilPuntos.NIVEL_CHOICES, default=PerfilPuntos.NIVEL_SEMILLA, verbose_name='nivel minimo requerido')
    
    class Meta:
        verbose_name = 'Beneficio'
        verbose_name_plural = 'Beneficios'
        ordering = ['costo_puntos']

    def __str__(self):
        return f"{self.nombre} - ({self.costo_puntos} pts)"
    
class Canje(models.Model):
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_APROBADO = 'aprobado'
    ESTADO_RECHAZADO = 'rechazado'
    ESTADO_ENTREGADO = 'entregado'

    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE,  '⏳ Pendiente de aprobación'),
        (ESTADO_APROBADO,   '✅ Aprobado'),
        (ESTADO_RECHAZADO,  '❌ Rechazado'),
        (ESTADO_ENTREGADO,  '🎁 Entregado'),
    ]
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='canjes', verbose_name='Estudiante')
    beneficio = models.ForeignKey(Beneficio, on_delete=models.PROTECT, related_name='canjes', verbose_name='beneficio solicitado')
    estado = models.CharField(max_length=10,choices=ESTADO_CHOICES,default=ESTADO_PENDIENTE)
    puntos_descontados = models.PositiveSmallIntegerField(verbose_name='puntos descontados')
    codigo_canje = models.UUIDField(null=True, blank=True, verbose_name='Codigo QR de canje')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_entrega    = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Canje'
        verbose_name_plural = 'Canjes'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"{self.usuario.nombre_completo} → {self.beneficio.nombre} [{self.get_estado_display()}]"

