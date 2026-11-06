from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('mascotas/', views.catalogo, name='catalogo'),
    path('mascotas/<int:pk>/', views.detalle, name='detalle'),
    path('adopcion/', views.adopcion, name='adopcion'),
    path('gestion/', views.gestion, name='gestion'),
    path('gestion/agregar/', views.agregar_mascota, name='agregar_mascota'),
    path('gestion/<int:pk>/editar/', views.editar_mascota, name='editar_mascota'),
]
