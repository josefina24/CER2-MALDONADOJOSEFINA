from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from .forms import MascotaForm
from .models import Especie, Mascota


def inicio(request):
    mascotas = Mascota.objects.exclude(estado='Adoptada').order_by('id')[:3]
    return render(request, 'refugio/inicio.html', {'mascotas': mascotas})


def catalogo(request):
    mascotas = Mascota.objects.exclude(estado='Adoptada').order_by('nombre')
    especies = Especie.objects.all().order_by('nombre')
    especie_seleccionada = None
    especie_id = request.GET.get('especie')
    if especie_id:
        # Un identificador que no existe o no es un número devuelve 404.
        if not especie_id.isdecimal():
            return render(request, '404.html', status=404)
        especie_seleccionada = get_object_or_404(Especie, pk=especie_id)
        mascotas = mascotas.filter(especie=especie_seleccionada)
    return render(request, 'refugio/catalogo.html', {
        'mascotas': mascotas,
        'especies': especies,
        'especie_seleccionada': especie_seleccionada,
    })


def detalle(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    # Una URL copiada tampoco muestra adoptadas a un visitante.
    if mascota.estado == 'Adoptada' and not request.user.has_perm('refugio.view_mascota'):
        raise Http404('Mascota no disponible en el catálogo público.')
    return render(request, 'refugio/detalle.html', {'mascota': mascota})


@login_required
@permission_required('refugio.view_mascota', raise_exception=True)
def gestion(request):
    mascotas = Mascota.objects.all().order_by('nombre')
    return render(request, 'refugio/gestion.html', {'mascotas': mascotas})


@login_required
@permission_required('refugio.add_mascota', raise_exception=True)
def agregar_mascota(request):
    if request.method == 'POST':
        form = MascotaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion')
    else:
        form = MascotaForm()
    return render(request, 'refugio/mascota_form.html', {
        'form': form, 'titulo': 'Agregar mascota',
    })


@login_required
@permission_required('refugio.change_mascota', raise_exception=True)
def editar_mascota(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    if request.method == 'POST':
        # instance indica que se modifica esta mascota y no se crea otra.
        form = MascotaForm(request.POST, instance=mascota)
        if form.is_valid():
            form.save()
            return redirect('gestion')
    else:
        form = MascotaForm(instance=mascota)
    return render(request, 'refugio/mascota_form.html', {
        'form': form, 'titulo': 'Modificar mascota',
    })


def adopcion(request):
    # Se conserva la página anterior como demostración, sin guardar solicitudes.
    mascotas = Mascota.objects.exclude(estado='Adoptada').order_by('nombre')
    return render(request, 'refugio/adopcion.html', {'mascotas': mascotas})
