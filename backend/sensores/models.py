from django.db import models

# Create your models here.

class LecturaSensor(models.Model):
    contenedor = models.ForeignKey('residuos.Contenedor', on_delete=models.CASCADE, related_name='lecturas', verbose_name="Contenedor")
    Distancia_cm = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Distancia medida (cm)")
    porcentaje_llenado = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Porcentaje de llenado (%)")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora de la lectura")
    token_dispositivo = models.CharField(max_length=64, verbose_name="Token del dispositivo")

    class Meta:
        verbose_name = "Lectura del Sensor"
        verbose_name_plural = "Lecturas de los Sensores"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.contenedor.nombre} -> {self.porcentaje_llenado}% - {self.timestamp.strftime('%d-%m-%Y %H:%M:%S')}"

    @property
    def estado(self):
        if self.porcentaje_llenado >= 95:
            return "Critico"  #rojo
        elif self.porcentaje_llenado >= 80:
            return "Ato"  #amarillo
        elif self.porcentaje_llenado >= 50:
            return "Medio"  #azul
        else:
            return "Bajo"  #verde
        
class AlertaContenedor(models.Model):

    NIVEL_AVISO = 'aviso' #80%
    NIVEL_URGENTE = 'critico' #95%

    NIVEL_CHOICES = [
        (NIVEL_AVISO, 'Aviso(80%)'),
        (NIVEL_URGENTE, 'Urgente(95%)'),
    ]

    contenedor = models.ForeignKey('residuos.Contenedor', on_delete=models.CASCADE, related_name='alertas', verbose_name="Contenedor")
    nivel = models.CharField(max_length=10, choices=NIVEL_CHOICES, verbose_name="Nivel de alerta")
    porcentaje_al_momento = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Porcentaje de llenado al momento de la alerta")
    atendida = models.BooleanField(default=False, verbose_name="Alerta atendida")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora de creación")
    fecha_atencion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha y hora de atención")
    notificado_municipalidad = models.BooleanField(default=False, verbose_name="municipalidad notificado")

    class Meta:
        verbose_name = "Alerta de Contenedor"
        verbose_name_plural = "Alertas de Contenedores"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{'🔴' if self.nivel == self.NIVEL_URGENTE else '🟡'} {self.contenedor.nombre} al {self.porcentaje_al_momento}%"