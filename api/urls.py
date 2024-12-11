""" from django.urls import path, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r'register', views.PersonaViewSet, basename='persona')

urlpatterns = [
    path('', include(router.urls)),
]
 """
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/update/', views.update_profile, name='update_profile'),  # Ruta para actualizar el perfil
    path('login_view/', views.login_view, name='login_view'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('datos/', views.datas, name='datas'),
    path('juntar/registrar_puntuacion/', views.registrar_puntuacion, name='registrar_puntuacion'),
    path('mejores-puntuaciones/', views.mejores_puntuaciones, name='mejores-puntuaciones'),
    path('solicitar-recuperacion/', views.solicitar_recuperacion_contrasena, name='solicitar-recuperacion'),
    path('resetear-contrasena/<uidb64>/<token>/', views.resetear_contrasena, name='reset-password-confirm'),

]





# urls.py





#  path('Recuperar/',views.Recuperar,name='Recuperar' )