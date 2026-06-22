from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class Usuario(AbstractUser):
    ROL_ESTUDIANTE = 'estudiante'
    ROL_COORDINADOR = 'coordinador'
    ROL_ADMIN = 'admin'

    ROL_CHOICES = [
        (ROL_ESTUDIANTE, 'Estudiante'),
        (ROL_COORDINADOR, 'Coordinador'),
        (ROL_ADMIN, 'Administrador')
    ]

    rut = models.CharField(max_length=12, unique=True, verbose_name='RUT')
    carrera = models.CharField(max_length=100, blank=True, null=True, verbose_name='Carrera')
    anio_cursando = models.PositiveIntegerField(null=True, blank=True, verbose_name='Año cursando')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default=ROL_ESTUDIANTE, verbose_name='Rol')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')
    foto = models.ImageField(upload_to='usuarios/fotos/', null=True, blank=True, verbose_name='Foto de perfil')

    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['username', 'email']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['carrera', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.rut} - {self.carrera}"
    
    @property
    def es_coordinador(self):
        return self.rol == self.ROL_COORDINADOR

