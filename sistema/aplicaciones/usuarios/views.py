from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView
from .forms import EmpleadoForm
from .models import Empleado
from django.contrib.auth.models import User  # Asegurar importación correcta de User

# Vista de inicio de sesión
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Credenciales inválidas')
    else:
        form = AuthenticationForm()
    
    return render(request, 'usuarios/login.html', {'form': form})

# Vista del Home
@login_required
def home_view(request):
    return render(request, 'usuarios/home.html', {'usuario': request.user.username})

# Función para verificar si el usuario es el dueño (admin)
def is_owner(user):
    return user.is_authenticated and user.is_staff

# Registrar Empleado (solo el dueño puede hacerlo)
@user_passes_test(is_owner)
@login_required

def registrar_empleado(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Verifica que el usuario no exista
            if User.objects.filter(username=username).exists():
                messages.error(request, "El nombre de usuario ya está en uso.")
                # Cambia aquí a 'usuarios/registrar_empleado.html'
                return render(request, 'usuarios/registrar_empleado.html', {'form': form})
            
            # Crear el usuario
            user = User.objects.create_user(username=username, password=password)
            
            # Asignar usuario al modelo Empleado
            empleado = form.save(commit=False)
            empleado.usuario = user
            empleado.save()
            
            messages.success(request, "Empleado registrado con éxito.")
            return redirect('home')
    else:
        form = EmpleadoForm()

    # Renderiza la misma plantilla en todos los casos
    return render(request, 'usuarios/registrar_empleado.html', {'form': form})


# Vista para listar empleados
@user_passes_test(is_owner)
@login_required
def lista_empleados(request):
    empleados = Empleado.objects.all()
    return render(request, 'usuarios/lista_empleados.html', {'empleados': empleados})

# Editar empleado
@user_passes_test(is_owner)
@login_required
def editar_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)

    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado actualizado exitosamente.')
            return redirect('lista_empleados')
    else:
        form = EmpleadoForm(instance=empleado)

    return render(request, 'usuarios/editar_empleado.html', {'form': form, 'empleado': empleado})

# Eliminar empleado
@user_passes_test(is_owner)
@login_required
def eliminar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    empleado.delete()
    messages.success(request, 'Empleado eliminado exitosamente.')
    return redirect('lista_empleados')

# Dashboard del jefe
@user_passes_test(is_owner)
@login_required
def jefe_dashboard(request):
    return render(request, 'usuarios/jefe_dashboard.html')

@login_required
def home_view(request):
    return render(request, 'usuarios/home.html') 
