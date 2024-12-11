from rest_framework import serializers
from .models import Persona, Puntuacion

class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}  # Evitar enviar contraseñas al frontend

    def create(self, validated_data):
        password = validated_data.pop('password')
        persona = Persona.objects.create(**validated_data)
        persona.set_password(password)
        return persona

class PuntuacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Puntuacion
        fields = ['id', 'user', 'intentos', 'fecha']
