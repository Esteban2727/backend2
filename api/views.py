# Vistas para autenticación y perfil
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Persona,Puntuacion
from rest_framework_simplejwt.tokens import RefreshToken
from .serializador import PersonaSerializer,PuntuacionSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model


@api_view(['POST'])
@permission_classes([AllowAny])
def registrar_puntuacion(request):
    user = request.user
    intentos = request.data.get('intentos')
    
    # Lógica para registrar la puntuación
    puntuacion = Puntuacion.objects.create(user=user, intentos=intentos)
    
    return Response({'status': 'success', 'puntuacion_id': puntuacion.id})


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_puntuaciones(request):
    user = request.user
    puntuaciones = Puntuacion.objects.filter(user=user)
    serializer = PuntuacionSerializer(puntuaciones, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = PersonaSerializer(data=request.data)
    if serializer.is_valid():
        persona = serializer.save()
        persona.set_password(serializer.validated_data['password'])
        persona.save()
        return Response({"message": "Registro exitoso"}, status=200)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    correo = request.data.get('correo')
    password = request.data.get('password')
    
    if not correo or not password:
        return Response({'error': 'Correo y contraseña son obligatorios.'}, status=400)

    try:
        persona = Persona.objects.get(correo=correo)
        
    except Persona.DoesNotExist:
        return Response({'error': 'El correo no está registrado.'}, status=400)
   
    if persona.check_password(password):
        # Generar tokens usando SimpleJWT
        refresh = RefreshToken.for_user(persona)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=200)
        
    else:
        return Response({'error': 'Contraseña incorrecta'}, status=400)

# Vista para obtener los datos del perfil del usuario autenticado


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def perfil(request):
    try:
        persona = request.user
        puntuacion = Puntuacion.objects.filter(user=persona).exclude(intentos=0).order_by('intentos').first()  # Obtener la mejor puntuación, excluyendo intentos de 0
        return Response({
            'message': 'Token válido',
            'user_id': persona.id,
            'correo': persona.correo,
            'username': persona.username,
            'puntuacion': PuntuacionSerializer(puntuacion).data if puntuacion else None
        }, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_profile(request):
    persona = request.user  
    print("ENTRO")
    print("Datos recibidos:", request.data)
    serializer = PersonaSerializer(persona, data=request.data, partial=True)  
    
    if serializer.is_valid():
        serializer.save()
        print("Datos actualizados:", serializer.data)
        
        # Si hay intentos en la solicitud, guardarlos en el modelo Puntuacion
        intentos = request.data.get('intentos')
        if intentos is not None:
            Puntuacion.objects.create(user=persona, intentos=intentos)
            
        return Response(serializer.data, status=200)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def datas(request):
    persona = list(Persona.objects.values())
    return Response(persona)

User = get_user_model()

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def mejores_puntuaciones(request):
    try:
        # Obtener las mejores puntuaciones de cada jugador, excluyendo intentos de 0
        puntuaciones = Puntuacion.objects.exclude(intentos=0).order_by('user', 'intentos')
        mejores_puntuaciones = []
        usuarios_procesados = set()

        for puntuacion in puntuaciones:
            if puntuacion.user not in usuarios_procesados:
                mejores_puntuaciones.append(puntuacion)
                usuarios_procesados.add(puntuacion.user)

        # Serializar las puntuaciones
        serialized_puntuaciones = PuntuacionSerializer(mejores_puntuaciones, many=True)

        # Agregar el nombre de usuario a cada puntuación
        for puntuacion_data in serialized_puntuaciones.data:
            user = User.objects.get(pk=puntuacion_data['user'])
            puntuacion_data['username'] = user.username

        return Response({
            'mejores_puntuaciones': serialized_puntuaciones.data
        }, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)






User = get_user_model()
@api_view(['POST'])
@permission_classes([AllowAny])
def solicitar_recuperacion_contrasena(request):
    correo = request.data.get('correo')
    try:
        usuario = User.objects.get(correo=correo)  # Usa el campo de correo correcto en tu modelo
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(usuario)
        uid = urlsafe_base64_encode(force_bytes(usuario.pk))

        url = f"http://localhost:5173/resetear-contrasena/{uid}/{token}"
        mensaje = f"Hola {usuario.username},\n\nPor favor, haz clic en el siguiente enlace para restablecer tu contraseña:\n{url}\n\nSi no solicitaste este cambio, por favor ignora este correo.\n\nGracias."
        
        send_mail(
            'Recuperación de contraseña',
            mensaje,
            'tu_correo@example.com',
            [correo],
            fail_silently=False,
        )
        return Response({'message': 'Correo de recuperación enviado'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'Correo no registrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def resetear_contrasena(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = User.objects.get(pk=uid)
        token_generator = PasswordResetTokenGenerator()
        if token_generator.check_token(usuario, token):
            nueva_contrasena = request.data.get('nueva_contrasena')
            usuario.set_password(nueva_contrasena)
            usuario.save()
            return Response({'message': 'Contraseña restablecida correctamente'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
