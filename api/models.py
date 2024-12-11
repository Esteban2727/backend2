from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password, check_password

# Manager para el modelo Persona
class PersonaManager(BaseUserManager):
    def create_user(self, correo, password=None, **extra_fields):
        if not correo:
            raise ValueError("El correo es obligatorio")
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("El superusuario debe tener is_staff=True")
        if not extra_fields.get('is_superuser'):
            raise ValueError("El superusuario debe tener is_superuser=True")

        return self.create_user(correo, password, **extra_fields)

# Modelo Persona extendido
class Persona(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100,unique=True)
    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=250)
    is_active = models.BooleanField(default=True)  # Indica si el usuario está activo
    is_staff = models.BooleanField(default=False)  # Indica acceso al admin
    date_joined = models.DateTimeField(auto_now_add=True)  # Fecha de registro

    objects = PersonaManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"bienvenido a la aplicación {self.username}"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

# Modelo Puntuacion
class Puntuacion(models.Model):
    user = models.ForeignKey(Persona, on_delete=models.CASCADE)
    intentos = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Puntuacion de {self.user.username} con {self.intentos} intentos el {self.fecha}'
    
