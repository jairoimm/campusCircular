from django.db import models
from django.conf import settings

# Create your models here.

class Contenedor(models.Model):
    AREA_CASINO = 'casino'
    AREA_GASTRONOMICA = 'gastronomia'
    AREA_PUNTO_VERDE = 'punto_verde'
    AREA_SALUD = 'salud'
    AREA_LOCALES = 'locales_comida'

    AREA_CHOICES = [
        (AREA_CASINO, 'Casino'),
        (AREA_GASTRONOMICA, 'Gastronomica'),
        (AREA_PUNTO_VERDE, 'Punto Verde'),
        (AREA_SALUD, 'Salud'),
        (AREA_LOCALES, 'Locales de Comida'),
    ]
    
    TIPO_ORGANICO = 'organico'
    TIPO_INORGANICO = 'inorganico'
    TIPO_PAPEL = 'papel'
    TIPO_MIXTO = 'mixto'
    TIPO_COMPOST = 'compost'

    TIPO_CHOICES = [
        (TIPO_ORGANICO, 'Organico'),
        (TIPO_INORGANICO, 'Inorganico / reciclable'),
        (TIPO_PAPEL, 'Papel  y carton'),
        (TIPO_MIXTO, 'Mixto'),
        (TIPO_COMPOST, 'Compostera'),
    ]

    nombre = models.CharField(max_length=100, verbose_name="Nombre del contenedor")
    area = models.CharField(max_length=30, choices=AREA_CHOICES, verbose_name="Área del campus")
    tipo_residuo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name="Tipo de residuo")
    codigo_qr = models.UUIDField(unique=True, editable=False, verbose_name="Código QR")
    altura_cm = models.PositiveSmallIntegerField(default=100, verbose_name="Altura del interior del contenedor (cm)")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_instalacion = models.DateField(auto_now_add=True, verbose_name="Fecha de instalación")

    class Meta:
        verbose_name = "Contenedor"
        verbose_name_plural = "Contenedores"
        ordering = ['area', 'tipo_residuo']
        
    def __str__(self):
        return f"{self.nombre} - {self.get_area_display()} - {self.get_tipo_residuo_display()}"
    
class RegistroResiduos(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="registros", verbose_name="Estudiante")
    contenedor = models.ForeignKey(Contenedor, on_delete=models.PROTECT, related_name="registros", verbose_name="Contenedor")
    peso_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Peso del residuo (kg)")
    peso_automatico = models.BooleanField(default=False, verbose_name="Peso registrado automáticamente")
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora del registro")
    puntos_obtenidos = models.PositiveIntegerField(default=0, verbose_name="Puntos obtenidos")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Registro de Residuo"
        verbose_name_plural = "Registros de Residuos"
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"{self.usuario.nombre_completo} - {self.contenedor.nombre} - {self.fecha_hora.strftime('%d-%m-%Y %H:%M:%S')}"
    