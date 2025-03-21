from django.shortcuts import render, redirect, get_object_or_404
from .models import Proceso, Respuesta, CuentaPorCobrar, CXC, RegistroFirma, RegistroCuenta, RegistroPregunta
from aplicaciones.carpetas.models import Carpeta
from .forms import ProcesoForm, RespuestaForm, CuentaPorCobrarForm, CXCForm, RegistroFirmaForm, RegistroCuentaForm, RegistroPreguntaForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def obtener_todas_subcarpetas(carpeta, visitadas=None):
    """Recupera todas las subcarpetas dentro de una carpeta, sin importar el nivel"""
    if visitadas is None:
        visitadas = set()
    
    subcarpetas = list(Carpeta.objects.filter(padre=carpeta))
    for sub in subcarpetas:
        if sub.id not in visitadas:  # Evita ciclos infinitos
            visitadas.add(sub.id)
            subcarpetas.extend(obtener_todas_subcarpetas(sub, visitadas))
    return subcarpetas

@login_required
def registrar_proceso(request, carpeta_id):
    """Registra un nuevo proceso y crea una carpeta con el mismo nombre dentro de la carpeta seleccionada,
    pero el proceso se guarda en la carpeta donde se hizo clic en 'Registrar Nuevo Proceso'."""

    carpeta_padre = get_object_or_404(Carpeta, id=carpeta_id)  # Carpeta donde se hizo clic (ejemplo: "Gualaceo")

    if request.method == "POST":
        form = ProcesoForm(request.POST)
        if form.is_valid():
            proceso = form.save(commit=False)

            # Validar si "carpeta_id" viene en la solicitud POST
            carpeta_destino_id = request.POST.get("carpeta_id")
            if not carpeta_destino_id:
                return render(request, "control_procesos/registrar_proceso.html", {
                    "form": form,
                    "subcarpetas": Carpeta.objects.filter(padre=carpeta_padre),
                    "carpeta_padre": carpeta_padre,
                    "error": "⚠ Debes seleccionar una subcarpeta para guardar el proceso.",
                })

            carpeta_destino = get_object_or_404(Carpeta, id=carpeta_destino_id)

            # Crear la carpeta con el nombre del proceso dentro de la carpeta seleccionada
            nueva_carpeta, created = Carpeta.objects.get_or_create(nombre=proceso.proceso, padre=carpeta_destino)

            # Guardar el proceso en la carpeta donde se hizo clic en "Registrar Nuevo Proceso"
            proceso.carpeta = carpeta_padre
            proceso.save()

            return redirect("carpetas:ver_carpeta", carpeta_id=carpeta_padre.id)

    else:
        form = ProcesoForm()

    # Obtener o crear la carpeta "Informes Periciales Grupo TACAE"
    informes_periciales, _ = Carpeta.objects.get_or_create(nombre="Informes Periciales Grupo TACAE", padre=None)
    subcarpetas = Carpeta.objects.filter(padre=informes_periciales)

    return render(request, "control_procesos/registrar_proceso.html", {
        "form": form,
        "subcarpetas": subcarpetas,
        "carpeta_padre": carpeta_padre,
    })

@login_required
def listar_procesos(request, carpeta_id):
    """Lista solo los procesos de la carpeta seleccionada."""
    carpeta = get_object_or_404(Carpeta, id=carpeta_id)
    procesos = Proceso.objects.filter(carpeta=carpeta)

    return render(request, 'control_procesos/listar_procesos.html', {
        'procesos': procesos,
        'carpeta': carpeta
    })

@login_required
def listar_carpetas(request):
    informes_periciales, _ = Carpeta.objects.get_or_create(nombre="Informes Periciales Grupo TACAE", padre=None)
    carpetas = Carpeta.objects.filter(padre=None)
    return render(request, 'carpetas/listar_carpetas.html', {'carpetas': carpetas})

@login_required
def ver_proceso(request, proceso_id):
    """
    Muestra los detalles de un proceso específico.
    """
    proceso = get_object_or_404(Proceso, id=proceso_id)
    return render(request, 'control_procesos/ver_proceso.html', {'proceso': proceso})

@login_required
def eliminar_proceso(request, proceso_id):
    """
    Elimina un proceso y redirige a la carpeta donde estaba almacenado.
    """
    proceso = get_object_or_404(Proceso, id=proceso_id)
    carpeta_id = proceso.carpeta.id  # Obtener la carpeta donde estaba el proceso
    proceso.delete()
    messages.success(request, "Proceso eliminado correctamente.")
    return redirect('carpetas:ver_carpeta', carpeta_id=carpeta_id)

@login_required
def editar_proceso(request, proceso_id):
    """Permite editar un proceso existente."""
    proceso = get_object_or_404(Proceso, id=proceso_id)

    if request.method == "POST":
        form = ProcesoForm(request.POST, instance=proceso)
        if form.is_valid():
            form.save()
            return redirect("carpetas:ver_carpeta", carpeta_id=proceso.carpeta.id)  # Redirigir a la carpeta donde está el proceso
    else:
        form = ProcesoForm(instance=proceso)

    return render(request, "control_procesos/editar_proceso.html", {"form": form, "proceso": proceso})


##############################Respuestas#####################################3

@login_required
def registrar_respuesta(request, carpeta_id):
    """Registra una nueva respuesta y la asocia a la carpeta correspondiente en 'Respuestas'"""
    carpeta_respuesta = get_object_or_404(Carpeta, id=carpeta_id)

    if request.method == "POST":
        form = RespuestaForm(request.POST)
        if form.is_valid():
            respuesta = form.save(commit=False)

            # 💡 Aquí aseguramos que la respuesta se guarda en la carpeta correcta
            respuesta.carpeta = carpeta_respuesta  # 🔥 Asignamos la carpeta de 'Respuestas'
            respuesta.save()

            messages.success(request, "✅ Respuesta registrada correctamente.")
            return redirect("carpetas:ver_carpeta", carpeta_id=carpeta_respuesta.id)

    else:
        form = RespuestaForm()

    return render(request, "control_procesos/registrar_respuesta.html", {
        "form": form,
        "carpeta": carpeta_respuesta
    })




def obtener_todas_subcarpetas(carpeta, lista=None):
    if lista is None:
        lista = [carpeta]
    for sub in carpeta.subcarpetas.all():
        lista.append(sub)
        obtener_todas_subcarpetas(sub, lista)
    return lista


@login_required
def listar_respuestas_subcarpeta(request, carpeta_id):
    """Lista las respuestas de una subcarpeta en 'Respuestas'."""
    carpeta = get_object_or_404(Carpeta, id=carpeta_id)
    
    # 🔥 IMPORTANTE: Filtrar solo respuestas que pertenecen a esta carpeta
    respuestas = Respuesta.objects.filter(carpeta=carpeta)

    return render(request, "control_procesos/listar_respuesta.html", {
        "carpeta": carpeta,
        "respuestas": respuestas
    })
    

@login_required
def listar_respuestas_por_nombre(request, carpeta_id):
    # Esta carpeta es la de la sección de Respuestas (por ejemplo, "Cuenca")
    carpeta_respuesta = get_object_or_404(Carpeta, id=carpeta_id)
    # Filtra las respuestas de los procesos que estén en una carpeta con el mismo nombre
    # y que pertenezcan a "Procesos Pendientes"
    respuestas = Respuesta.objects.filter(
        proceso__carpeta__nombre=carpeta_respuesta.nombre,
        proceso__carpeta__padre__nombre="Procesos Pendientes"
    )
    return render(request, 'control_procesos/listar_respuestas_subcarpeta.html', {
        'carpeta': carpeta_respuesta,
        'respuestas': respuestas,
    })
    
    
######################### CUENTAS POR COBRAR #############################




@login_required
def registrar_cuenta_por_cobrar(request, carpeta_id):
    """Registra un nuevo cobro, permitiendo seleccionar un proceso de forma organizada."""
    
    carpeta = get_object_or_404(Carpeta, id=carpeta_id)

    if request.method == "POST":
        form = CuentaPorCobrarForm(request.POST)
        if form.is_valid():
            cuenta = form.save(commit=False)
            cuenta.carpeta = carpeta
            cuenta.save()
            return redirect("carpetas:ver_carpeta", carpeta_id=carpeta.id)
    
    else:
        form = CuentaPorCobrarForm()

    # 🌟 Obtener procesos organizados por carpeta
    carpetas_con_procesos = {}
    carpetas = Carpeta.objects.all()
    
    for carpeta in carpetas:
        procesos = Proceso.objects.filter(carpeta=carpeta)
        if procesos.exists():
            carpetas_con_procesos[carpeta] = procesos

    return render(request, "control_procesos/registrar_cuenta.html", {
        "form": form,
        "carpeta": carpeta,
        "carpetas_con_procesos": carpetas_con_procesos,  # Pasamos los procesos organizados
    })


def listar_cuentas_por_cobrar(request, carpeta_id):
    carpeta = get_object_or_404(Carpeta, id=carpeta_id)
    cuentas = carpeta.cuentas_por_cobrar.all()  # CORRECTO ✅



    return render(request, "control_procesos/listar_cuentas.html", {
        "cuentas": cuentas,
        "carpeta": carpeta
    })



###############################CXC#########################
@login_required
def crear_cxc_tacae(request, carpeta_id):
    # Obtener la subcarpeta actual
    carpeta = get_object_or_404(Carpeta, id=carpeta_id)
    
    if request.method == 'POST':
        form = CXCForm(request.POST)
        if form.is_valid():
            nueva_cxc = form.save(commit=False)
            nueva_cxc.carpeta = carpeta  # Se asocia a la subcarpeta
            nueva_cxc.save()
            return redirect('carpetas:ver_carpeta', carpeta_id=carpeta.id)
    else:
        form = CXCForm()
    
    return render(request, 'control_procesos/crear_cxc.html', {
        'form': form,
        'carpeta': carpeta
    })
@login_required
def editar_cxc(request, cxc_id):
    """
    Vista para editar (y actualizar) un registro de CXC.
    Se muestra el formulario con los datos actuales y, al enviarlo,
    se actualiza el registro.
    """
    cxc = get_object_or_404(CXC, id=cxc_id)
    if request.method == 'POST':
        form = CXCForm(request.POST, instance=cxc)
        if form.is_valid():
            form.save()
            # Redirige a la vista de la carpeta asociada a este registro
            return redirect('carpetas:ver_carpeta', carpeta_id=cxc.carpeta.id)
    else:
        form = CXCForm(instance=cxc)
    return render(request, 'control_procesos/editar_cxc.html', {'form': form, 'cxc': cxc})


@login_required
def eliminar_cxc(request, cxc_id):
    """
    Vista para eliminar un registro de CXC.
    Se muestra una confirmación y, al enviar el formulario,
    se elimina el registro.
    """
    cxc = get_object_or_404(CXC, id=cxc_id)
    if request.method == 'POST':
        cxc.delete()
        # Redirige a la vista de la carpeta asociada tras la eliminación
        return redirect('carpetas:ver_carpeta', carpeta_id=cxc.carpeta.id)
    return render(request, 'control_procesos/eliminar_cxc.html', {'cxc': cxc})



################firmas#######################
def crear_firma(request, carpeta_id):
    """
    Vista para crear un nuevo registro de firma en la carpeta especificada.
    """
    carpeta = get_object_or_404(Carpeta, id=carpeta_id)
    if request.method == 'POST':
        form = RegistroFirmaForm(request.POST)
        if form.is_valid():
            firma = form.save(commit=False)
            firma.carpeta = carpeta
            firma.save()
            return redirect('carpetas:ver_carpeta', carpeta_id=carpeta.id)
    else:
        form = RegistroFirmaForm()
    return render(request, 'control_procesos/crear_firma.html', {'form': form, 'carpeta': carpeta})

def editar_firma(request, firma_id):
    """
    Vista para editar un registro de firma existente.
    """
    firma = get_object_or_404(RegistroFirma, id=firma_id)
    if request.method == 'POST':
        form = RegistroFirmaForm(request.POST, instance=firma)
        if form.is_valid():
            form.save()
            return redirect('carpetas:ver_carpeta', carpeta_id=firma.carpeta.id)
    else:
        form = RegistroFirmaForm(instance=firma)
    return render(request, 'control_procesos/editar_firma.html', {'form': form, 'firma': firma})

def eliminar_firma(request, firma_id):
    """
    Vista para eliminar un registro de firma.
    """
    firma = get_object_or_404(RegistroFirma, id=firma_id)
    carpeta_id = firma.carpeta.id
    firma.delete()
    return redirect('carpetas:ver_carpeta', carpeta_id=carpeta_id)

#######################registrar cuentas ########################3
def crear_cuenta_especial(request, carpeta_id):
    """Crea un nuevo registro de 'Cuenta' en la carpeta especificada."""
    carpeta = get_object_or_404(Carpeta, id=carpeta_id)
    if request.method == 'POST':
        form = RegistroCuentaForm(request.POST)
        if form.is_valid():
            cuenta = form.save(commit=False)
            cuenta.carpeta = carpeta
            cuenta.save()
            return redirect('carpetas:ver_carpeta', carpeta_id=carpeta.id)
    else:
        form = RegistroCuentaForm()
    return render(request, 'control_procesos/crear_cuenta_especial.html', {
        'carpeta': carpeta,
        'form': form
    })

def editar_cuenta_especial(request, cuenta_id):
    """Edita un registro de 'Cuenta' existente."""
    cuenta = get_object_or_404(RegistroCuenta, id=cuenta_id)
    if request.method == 'POST':
        form = RegistroCuentaForm(request.POST, instance=cuenta)
        if form.is_valid():
            form.save()
            return redirect('carpetas:ver_carpeta', carpeta_id=cuenta.carpeta.id)
    else:
        form = RegistroCuentaForm(instance=cuenta)
    return render(request, 'control_procesos/editar_cuenta_especial.html', {
        'form': form,
        'cuenta': cuenta
    })

def eliminar_cuenta_especial(request, cuenta_id):
    """Elimina un registro de 'Cuenta'."""
    cuenta = get_object_or_404(RegistroCuenta, id=cuenta_id)
    carpeta_id = cuenta.carpeta.id
    cuenta.delete()
    return redirect('carpetas:ver_carpeta', carpeta_id=carpeta_id)


#################### pregunta ###############



def crear_pregunta(request, carpeta_id):
    """Crea un nuevo registro de Pregunta en la carpeta especificada."""
    carpeta = get_object_or_404(Carpeta, id=carpeta_id)
    if request.method == 'POST':
        form = RegistroPreguntaForm(request.POST)
        if form.is_valid():
            pregunta_obj = form.save(commit=False)
            pregunta_obj.carpeta = carpeta
            pregunta_obj.save()
            return redirect('carpetas:ver_carpeta', carpeta_id=carpeta.id)
    else:
        form = RegistroPreguntaForm()
    return render(request, 'control_procesos/crear_pregunta.html', {
        'carpeta': carpeta,
        'form': form
    })

def editar_pregunta(request, pregunta_id):
    """Edita un registro de Pregunta existente."""
    pregunta_obj = get_object_or_404(RegistroPregunta, id=pregunta_id)
    if request.method == 'POST':
        form = RegistroPreguntaForm(request.POST, instance=pregunta_obj)
        if form.is_valid():
            form.save()
            return redirect('carpetas:ver_carpeta', carpeta_id=pregunta_obj.carpeta.id)
    else:
        form = RegistroPreguntaForm(instance=pregunta_obj)
    return render(request, 'control_procesos/editar_pregunta.html', {
        'form': form,
        'pregunta_obj': pregunta_obj
    })

def eliminar_pregunta(request, pregunta_id):
    """Elimina un registro de Pregunta."""
    pregunta_obj = get_object_or_404(RegistroPregunta, id=pregunta_id)
    carpeta_id = pregunta_obj.carpeta.id
    pregunta_obj.delete()
    return redirect('carpetas:ver_carpeta', carpeta_id=carpeta_id)



