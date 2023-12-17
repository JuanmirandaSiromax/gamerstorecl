from decimal import Decimal, DecimalException
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Juego, Categoria, Pedidos , UserProfile
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import role_requiered
from django.contrib.auth.models import User
from django.conf.urls import handler404
from .models import MensajeContacto

# Create your views here.

# definicion sesion de usuarios y perfil
def index(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        clave = request.POST.get('pass')

        user = authenticate(request, username = usuario, password = clave)
        if user is not None:
            # Autenticación exitosa
            login(request, user)
            try:
                profile = user.userprofile  # Obtén el perfil de usuario
                request.session['perfil'] = profile.role
            except UserProfile.DoesNotExist:
                # Si el perfil de usuario no existe, puedes manejarlo aquí
                messages.error(request, 'El perfil de usuario no está configurado correctamente.')
                return redirect('principal')
            
            return redirect('home')
        else:
            context = {
                'error': 'Error, inténtelo nuevamente'
            }
            return render(request, 'auth/index.html', context)

    return render(request, 'auth/index.html')

# Vista Home
@login_required
def home(request):
    if request.user.is_authenticated:
        # Obtener el perfil del usuario
        perfil = request.user.username
        juegos = Juego.objects.all()
        print(juegos)
        codigo_invent = request.POST.get('codigo_invent')
        juego_nombre = request.POST.get('juego_nombre')
        juego_precio = request.POST.get('juego_precio')
        juego_imagen_url = request.POST.get('juego_imagen_url')

        carrito = request.session.get('carrito', [])

        juego_data = {
            'codigo_invent': codigo_invent,
            'nombre': juego_nombre,
            'precio': juego_precio,
            'imagen_url': juego_imagen_url,
        }
        request.session['juego'] = juego_data

        context = {
            'juegos': juegos,
            'perfil': perfil,
            'carrito': carrito,
        }

    return render(request, 'auth/home.html', context)

# Vista Lista de usuarios
@login_required
def listado_usuarios(request):
    users = User.objects.all()
    perfil = request.user.profile.role if hasattr(request.user, 'profile') else None

    context = {
        'user': users,
        'perfil': perfil,
    }

    return render(request, 'auth/listado_usuarios.html', context)
    
# Vista Registro de Usuario
def formulario(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        email = request.POST['email']
        # Validar los datos ingresados 
        if not username:
            messages.error(request, 'Nombre de usuario es obligatorio')
            return redirect('formulario')
        
        if len(password) < 6 or len(password) > 16:
            messages.error(request, 'La contraseña debe tener entre 6 y 16 caracteres')
            return redirect('formulario')
        
        if not any(char.isupper() for char in password):
            messages.error(request, 'La contraseña debe contener al menos una letra mayúscula')
            return redirect('formulario')

        # Verificar si el nombre de usuario ya existe
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso')
            return redirect('formulario')
        
        if password != password2:
            messages.error(request, 'La contraseña debe ser iguales')
            return redirect('formulario')
        
        user = User.objects.create_user(
            first_name=first_name,
            username=username,
            password=password,
            email=email
            )
        role = 'cliente'
        UserProfile.objects.create(user=user, role=role)

        authenticated_user = authenticate(request, username=username, password=password)
        if authenticated_user:
            login(request, authenticated_user)

        messages.success(request, 'Se ha creado la cuenta correctamente como cliente')

        return redirect('home')
        
    else:
        return render(request, 'auth/formulario.html')  

# Vista Editar Datos de Usuarios
@role_requiered('admin')
def editar_datos(request,id):
    
        usuario = get_object_or_404(User, id=id)
        
        if request.method == 'POST':
            first_name = request.POST['first_name']
            username = request.POST['username']
            password = request.POST['password']
            email = request.POST['email']
            role = request.POST['role'] 

            usuario.first_name = first_name
            usuario.username = username
            usuario.set_password(password)
            usuario.email = email
            usuario.userprofile.role = role
            usuario.userprofile.save()  
            usuario.save()

            messages.success(request, 'Usuario editado exitosamente.')
            return redirect('listado_usuarios')
        return render(request, 'auth/editar_datos.html', {'usuario': usuario})


def recuperar_contrasenna(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        new_pass= "123123"

        try:
            usuario = User.objects.get(email=correo)
            usuario.set_password(new_pass)
            usuario.save()
            messages.success(request, 'La contraseña se actualizo con exito')
            return redirect('index')
        except User.DoesNotExist:
            messages.error(request,'No se encontro ningun usuario con ese correo Electronico')

    return render(request, 'auth/recuperar_contrasenna.html')

@role_requiered('admin')
def eliminar_usuario(request, id):
    usuario = get_object_or_404(User, id=id)
    usuario.delete()
    messages.success(request, 'Se ha Eliminado Correctamente')
    return redirect('listado_usuarios')

@role_requiered('admin','cliente')
def logout_view (request):
    logout(request)
    return render(request, 'juegos/principal.html')

def cerrar_sesion(request):
    logout(request)
    return redirect('index')

# definiciones para juegos 
@login_required
def principal(request):
    return render(request, 'juegos/principal.html')

@login_required
def accion(request):
        
    juegos_accion = Juego.objects.filter(categoria__nombre='ACCION')
    perfil = request.session.get('perfil')
    context = {
        'juegos_accion': juegos_accion,
        'perfil': perfil,
    }
    return render(request, 'juegos/accion.html',context)

@login_required
def supervivencia(request):

    juegos_supervivencia = Juego.objects.filter(categoria__nombre='SUPERVIVENCIA')
    perfil = request.session.get('perfil')
    context = {
        'juegos_supervivencia': juegos_supervivencia,
        'perfil': perfil,
    }
    return render(request, 'juegos/supervivencia.html', context)

@login_required
def terror(request):

    juegos_terror = Juego.objects.filter(categoria__nombre='TERROR')
    perfil = request.session.get('perfil')
    context = {
        'juegos_terror': juegos_terror,
        'perfil': perfil,
    }
    return render(request, 'juegos/terror.html',context)
@login_required
def aventura(request):

    juegos_aventura = Juego.objects.filter(categoria__nombre='AVENTURA')
    perfil = request.session.get('perfil')
    context = {
        'juegos_aventura': juegos_aventura,
        'perfil': perfil,
    }
    return render(request, 'juegos/aventura.html',context)
@login_required
def carreras(request):

    juegos_carreras = Juego.objects.filter(categoria__nombre='CARRERAS')
    perfil = request.session.get('perfil')
    context = {
        'juegos_carreras': juegos_carreras,
        'perfil': perfil,
    }
    return render(request, 'juegos/carreras.html',context)

@login_required
def compra(request):
    return render(request, 'juegos/carrito.html')

    
@login_required
def juegos_show(request, id):
    if request.user.is_authenticated:
        perfil = request.user.username
        juego = get_object_or_404(Juego, id=id)

        if request.method == 'POST':
            # Validar el formulario (puedes agregar más validaciones según sea necesario)
            if 'cantidad' in request.POST:
                cantidad = int(request.POST['cantidad'])
            else:
                cantidad = 1

            # Agregar el juego al carrito
            carrito = request.session.get('carrito', [])
            carrito.append({
                'codigo_invent': juego.codigo_invent,
                'nombre': juego.nombre,
                'precio': juego.precio,
                'imagen_url': juego.imagen.url,
                'cantidad': cantidad,
            })
            request.session['carrito'] = carrito

            # Mensaje de éxito
            messages.success(request, f'Se agregaron {cantidad} {juego.nombre} al carrito.')

        carrito = request.session.get('carrito', [])
        context = {
            'juego': juego,
            'perfil': perfil,
            'carrito': carrito,
        }

        return render(request, 'juegos/juegos_show.html', context)


@login_required
def listado_juegos(request):
    # Verificar si el usuario está autenticado
    if request.user.is_authenticated:
        # Obtener el perfil del usuario
        perfil = request.user.username
        juegos = Juego.objects.all()

        context = {
            'juegos': juegos,
            'perfil': perfil,
        }
        return render(request, 'juegos/listado_juegos.html', context)
    else:
        # El usuario no está autenticado, puedes manejarlo de acuerdo a tus necesidades
        return HttpResponse("Usuario no autenticado")
    
@login_required
def juegos_editar(request, id):
    juego = get_object_or_404(Juego, id=id)

    if request.method == 'POST':
        categoria_id = request.POST.get('categoria')
        categoria = get_object_or_404(Categoria, id=categoria_id)

        # Asegúrate de utilizar get() para acceder a los valores del formulario
        juego.nombre = request.POST.get('nombre', '')
        juego.codigo = request.POST.get('codigo_invent', '')
        juego.descripcion = request.POST.get('descripcion', '')

        # Asegúrate de manejar adecuadamente la entrada del usuario, como convertir a decimal si es necesario
        precio = request.POST.get('precio', '')
        try:
            juego.precio = Decimal(precio)
        except DecimalException:
            # Maneja el caso en que el valor no sea un decimal válido
            pass

        juego.categoria = categoria

        if 'imagen' in request.FILES:
            juego.imagen = request.FILES['imagen']

        juego.save()
        messages.success(request, 'Se ha actualizado correctamente')

    categorias = Categoria.objects.all()
    context = {
        'juego': juego,
        'categorias': categorias,
    }
    return render(request, 'juegos/juegos_editar.html', context)


   
@login_required
def crear_juego(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        codigo_invent = request.POST['codigo_invent']
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        precio = request.POST['precio']
        categoria_id = request.POST['categoria']
        imagen = request.FILES.get('imagen')

        # Verificar si ya existe un juego con el mismo código de inventario
        if Juego.objects.filter(codigo_invent=codigo_invent).exists():
            messages.error(request, 'Ya existe un juego con ese código de inventario.')
            return redirect('crear_juego')  # Redirigir a la página de creación de juego

        # Si no existe, crear el nuevo juego
        juego = Juego(
            codigo_invent=codigo_invent,
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            categoria_id=categoria_id,
            imagen=imagen
        )
        juego.save()

        messages.success(request, 'El juego se ha creado correctamente.')
        return redirect('vista_juegos')  # Redirigir a la página de visualización de juegos

    categorias = Categoria.objects.all()
    
    context = {
        'categorias': categorias
    }
    
    return render(request, 'juegos/crearjuego.html', context)
@login_required
def eliminar_juego(request, id):
    juego = get_object_or_404(Juego, id=id)
    juego.delete()
    messages.success(request, 'Se ha Eliminado Correctamente')
    return redirect('listado_juegos')

@login_required
def vista_carrito(request):

    if request.method == 'POST':
        codigo_invent = request.POST.get('codigo_invent')
        print(codigo_invent)
        juego_nombre = request.POST.get('juego_nombre')
        juego_precio = request.POST.get('juego_precio')
        juego_imagen_url = request.POST.get('juego_imagen_url')
        
        carrito = request.session.get('carrito', [])

        if juego_nombre != None :
            carrito.append({
                'codigo_invent': codigo_invent,
                'nombre': juego_nombre,
                'precio': int(juego_precio),
                'cantidad': 1,
                'imagen_url': juego_imagen_url,
            })
        request.session['carrito'] = carrito

        if 'eliminar_del_carrito' in request.POST:
            codigo_invent_a_eliminar = request.POST.get('codigo_invent')
            contador = 0
            
            for index, item in enumerate(carrito):
                if item['codigo_invent'] == codigo_invent_a_eliminar:
                    carrito.pop(index)
                    
            request.session['carrito'] = carrito

        if 'continuar' in request.POST:
            return redirect('metodo_pago')
    
    carrito = request.session.get('carrito', [])
    subtotal = sum(int(item['precio']) for item in carrito)
    
    request.session['subtotal'] = subtotal

    return render(request, 'juegos/carrito.html', {'carrito': carrito})

def metodo_pago(request):
    if request.method == 'POST':
        metodo_de_pago = request.POST.get('metodo_de_pago')

        if not metodo_de_pago:
            messages.error(request, 'Debe seleccionar un método de pago antes de continuar.')
            return redirect('metodo_pago')

    return render(request, 'auth/metodo_pago.html')

def venta_exitosa(request):
    # Obtener la información del carrito actual de la sesión
    carrito = request.session.get('carrito', [])

    # Calcular el subtotal
    subtotal_total = sum(item['cantidad'] * item['precio'] for item in request.session.get('carrito', []))

    # Pasar la información al contexto
    context = {
        'carrito': request.session.get('carrito', []),
        'subtotal_total': subtotal_total,
    }

    return render(request, 'auth/venta_realizada.html', context)


# Vista en caso de que no encuentra una ruta válida
def vista_error_404(request, exception):
    return render(request, '404.html', status=404)

@login_required
def contacto(request):
    mensaje_exito = None

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '')
        correo = request.POST.get('correo', '')
        mensaje_texto = request.POST.get('mensaje', '')

        # Crea un objeto MensajeContacto y guárdalo en la base de datos
        mensaje_contacto = MensajeContacto(nombre=nombre, correo=correo, mensaje=mensaje_texto)
        mensaje_contacto.save()

        mensaje_exito = f'Gracias por contactarte con nosotros, {nombre}. Te contactaremos a la brevedad.'

        # Redirige a la misma página con el mensaje de éxito
        return render(request, 'auth/contacto.html', {'mensaje_exito': mensaje_exito})

    return render(request, 'auth/contacto.html', {'mensaje_exito': mensaje_exito})

def procesar_pedido(request):
    if request.method == 'POST':
        # Obtener datos del carrito desde la sesión
        carrito = request.session.get('carrito', [])

        # Obtener el usuario actual
        usuario_actual = request.user

        # Procesar cada elemento del carrito
        for item in carrito:
            nombre = item['nombre']
            cantidad = item['cantidad']
            precio_unitario = item['precio']
            total = cantidad * precio_unitario

            # Crear instancia de Pedido y guardar en la base de datos
            pedido = Pedidos(nombre=nombre, cantidad=cantidad, total=total, usuario=usuario_actual)
            pedido.save()

        # Limpiar el carrito después de procesar el pedido
        del request.session['carrito']
        messages.success(request, 'Pedido procesado exitosamente.')
        return redirect('pagina_de_confirmacion')  # Redirigir a la página de confirmación

    else:
        return render(request, 'error.html') 