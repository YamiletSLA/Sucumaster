from datetime import timedelta
from urllib import request

from flask import Flask,render_template,request,redirect,url_for,flash,session,abort
from flask_bootstrap import Bootstrap
from modelo.Dao import db, Categoria, Producto, Usuario, tipoPago, Transportes, Ventas, Pedidos, DetallePedidos, Clientes
from flask_login import login_required,login_user,logout_user,current_user,LoginManager
import json

app = Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:root@localhost/sucumaster'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.secret_key='Cl4v3'
#Implementación de la gestion de usuarios con flask-login
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='mostrar_login'
login_manager.login_message='¡ Tu sesión expiró !'
login_manager.login_message_category="info"

# Urls defininas para el control de usuario

@app.route("/")
def inicio():
    #return "Bienvenido a la tienda en linea Shopitesz"
    return render_template('usuarios/login.html')

@app.route('/Usuarios/iniciarSesion')
def mostrar_login():
    if current_user.is_authenticated:
        return render_template('principal.html')
    else:
        return render_template('usuarios/login.html')

@login_manager.user_loader
def cargar_usuario(id):
    return Usuario.query.get(int(id))

@app.route('/Usuarios/nuevo')
def nuevoUsuario():
    if current_user.is_authenticated and not current_user.is_admin():
        return render_template('principal.html')
    else:
        return render_template('usuarios/registrarCuenta.html')

@app.route('/Usuarios/agregar',methods=['post'])
def agregarUsuario():
    try:
        usuario=Usuario()
        usuario.nombreCompleto=request.form['nombreCompleto']
        usuario.nombreUsuario=request.form['nombreUsuario']
        usuario.direccion=request.form['direccion']
        usuario.contraseña=request.form['contraseña']
        usuario.estatus = 'A'
        usuario.tipoUsuario=request.values.get("tipo","Vendedor")

        usuario.agregar()
        flash('¡ Usuario registrado con exito')
    except:
        flash('¡ Error al agregar al usuario !')
    return render_template('usuarios/registrarCuenta.html')


@app.route("/Usuarios/validarSesion",methods=['POST'])
def login():
    nombreUsuario=request.form['nomUsu']
    contraseña=request.form['password']
    usuario=Usuario()
    user=usuario.validar(nombreUsuario,contraseña)
    if user!=None:
        login_user(user)
        return render_template('principal.html')
    else:
        flash('Nombre de usuario o contraseña incorrectos')
        return render_template('usuarios/login.html')

@app.route('/Usuarios/cerrarSesion')
@login_required
def cerrarSesion():
    logout_user()
    return redirect(url_for('mostrar_login'))

@app.route('/Usuarios/verPerfil')
@login_required
def consultarUsuario():
    return render_template('usuarios/editar.html')

@app.route('/Usuarios/Clientes')
@login_required
def consultarClientes():
    if current_user.is_authenticated and current_user.is_admin():
        user=Usuario()
        return render_template('usuarios/clientes.html',user=user.consultaUsuarios())
    else:
        return render_template('usuarios/login.html')
@app.route('/Usuarios/Vendedores')
@login_required
def consultarVendedores():
    if current_user.is_authenticated and current_user.is_admin():
        user=Usuario()
        return render_template('usuarios/vendedores.html',user=user.consultaUsuarios())
    else:
        return render_template('usuarios/login.html')
@app.route('/Usuarios/Admin')
@login_required
def consultarAdmin():
    if current_user.is_authenticated and current_user.is_admin():
        user=Usuario()
        return render_template('usuarios/admins.html',user=user.consultaUsuarios())
    else:
        return render_template('usuarios/login.html')
#fin del manejo de usuarios

@app.route('/Usuarios/<int:id>')
@login_required
def consultarUnUsuario(id):
    if current_user.is_authenticated and current_user.is_admin():
        user=Usuario()
        return render_template('usuarios/editarUsu.html',user=user.consultaIndividual(id))
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/Usuarios/modificar',methods=['POST'])
@login_required
def modificarUsuario():
    if current_user.is_authenticated:
        try:
            user=Usuario()
            user.idUsuario=request.form['ID']
            user.nombreCompleto=request.form['nombre']
            user.email=request.form['email']
            user.direccion=request.form['direccion']
            user.genero=request.form['genero']
            user.tipo=request.form['tipo']
            user.editarUsua()
            flash('¡ Usuario editado con exito !')
        except:
            flash('¡ Error al editar el usuario !')

        if user.tipo == 'Almacenista':
            return redirect(url_for('consultarClientes'))
        else:
            if user.tipo == 'Vendedor':
                return redirect(url_for('consultarVendedores'))
            else :
                return redirect(url_for('consultarAdmin'))

    else:
        return redirect(url_for('mostrar_login'))
#PRODUCTOS

@app.route("/productos")
def consultarProductos():
    producto=Producto()
    return render_template("productos/consultaGeneral.html",productos=producto.consultaGeneral())

@app.route("/productos/categorias")
def productosPorCategoria():
    categoria=Categoria()
    return render_template('productos/productosPorCategoria.html',categorias=categoria.consultaGeneral())

@app.route("/productos/categoria/<int:id>")
def consultarProductosPorCategoria(id):
    producto=Producto()
    if id==0:
        lista=producto.consultaGeneral()
    else:
        lista=producto.consultarProductosPorCategoria(id)
    #print(lista)
    listaProductos=[]
    #Generacion de un diccionario para convertir los datos a JSON
    for prod in lista:
        prod_dic={'idProducto':prod.idProducto,'nombre':prod.nombre,'descripcion':prod.descripcion,'precio':prod.precio}
        listaProductos.append(prod_dic)
    #print(listaProductos)
    var_json=json.dumps(listaProductos)
    return var_json

@app.route('/producto/<int:id>')
def consultarProducto(id):
    if current_user.is_authenticated and  current_user.is_admin():
        prod=Producto()
        prod.consultaIndividual(id)
        return render_template('productos/Modificar.html',prod=prod.consultaIndividual(id))
    else:
        msg={"estatus":"error","mensaje":"Debes iniciar sesion"}
        return json.dumps(msg)

@app.route('/Productos/nuevo')
@login_required
def nuevoProducto():
    if current_user.is_authenticated and current_user.is_admin():
            return render_template('productos/Registrar.html')
    else:
        abort(404)

@app.route('/Productos/agregar',methods=['post'])
@login_required
def agregarProducto():
    try:
        if current_user.is_authenticated:
            if current_user.is_admin():
                try:
                    prod=Producto()
                    prod.idCategorias=request.form['categoria']
                    prod.nombre=request.form['nombre']
                    prod.descripcion=request.form['desc']
                    prod.precio=request.form['precio']
                    prod.agregar()
                    flash('¡ Producto agregada con exito !')
                except:
                    flash('¡ Error al agregar el producto !')
                return redirect(url_for('consultarProductos'))
            else:
                abort(404)

        else:
            return redirect(url_for('mostrar_login'))
    except:
        abort(500)

@app.route('/Productos/editar',methods=['POST'])
@login_required
def editarProducto():
    if current_user.is_authenticated and current_user.is_admin():
        try:
            prod=Producto()
            prod.idCategorias=request.form['idCategorias']
            prod.nombre=request.form['nombre']
            prod.descripcion = request.form['desc']
            prod.precio = request.form['precio']
            prod.editar()
            flash('¡ Producto editado con exito !')
        except:
            flash('¡ Error al editar el producto !')

        return redirect(url_for('consultarProductos'))
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/Productos/eliminar/<int:id>')
@login_required
def eliminarProducto(id):
    if current_user.is_authenticated and current_user.is_admin():
        try:
            prod=Producto()
            prod.eliminar(id)
            flash('Producto eliminado con exito')
        except:
            flash('Error al eliminar el producto')
        return redirect(url_for('consultarProductos'))
    else:
        return redirect(url_for('mostrar_login'))


#Categorias
@app.route('/Categorias')
def consultaCategorias():
    cat=Categoria()
    return render_template('categorias/consultaGeneral.html',categorias=cat.consultaGeneral())


@app.route('/Categorias/nueva')
@login_required
def nuevaCategoria():
    if current_user.is_authenticated and current_user.is_admin():
            return render_template('categorias/agregar.html')
    else:
        abort(404)

@app.route('/Categorias/agregar',methods=['post'])
@login_required
def agregarCategoria():
    try:
        if current_user.is_authenticated:
            if current_user.is_admin():
                try:
                    cat=Categoria()
                    cat.nombre=request.form['nombre']
                    cat.agregar()
                    flash('¡ Categoria agregada con exito !')
                except:
                    flash('¡ Error al agregar la categoria !')
                return redirect(url_for('consultaCategorias'))
            else:
                abort(404)

        else:
            return redirect(url_for('mostrar_login'))
    except:
        abort(500)


@app.route('/Categorias/<int:id>')
@login_required
def consultarCategoria(id):
    if current_user.is_authenticated and current_user.is_admin():
        cat=Categoria()
        return render_template('categorias/editar.html',cat=cat.consultaIndividual(id))
    else:
        return redirect(url_for('mostrar_login'))


@app.route('/Categorias/editar',methods=['POST'])
@login_required
def editarCategoria():
    if current_user.is_authenticated and current_user.is_admin():
        try:
            cat=Categoria()
            cat.idCategorias=request.form['id']
            cat.nombre=request.form['nombre']
            cat.editar()
            flash('¡ Categoria editada con exito !')
        except:
            flash('¡ Error al editar la categoria !')

        return redirect(url_for('consultaCategorias'))
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/Categorias/eliminar/<int:id>')
@login_required
def eliminarCategoria(id):
    if current_user.is_authenticated and current_user.is_admin():
        try:
            categoria=Categoria()
            categoria.eliminar(id)
            #categoria.eliminacionLogica(id)
            flash('Categoria eliminada con exito')
        except:
            flash('Error al eliminar la categoria')
        return redirect(url_for('consultaCategorias'))
    else:
        return redirect(url_for('mostrar_login'))

#Fin del crud de categorias
# PEDIDOS

@app.route('/Pedidos')
def consultarPedidos():
    ped=Pedidos()
    return render_template('pedidos/consultaGeneral.html',pedidos=ped.consultaGeneral())

@app.route('/Pedidos/agregar',methods=['post'])
@login_required
def agregarPedidos():
    try:
        if current_user.is_authenticated:
            if current_user.is_authenticated:
                try:
                    ped=Pedidos()
                    ped.idComprador=request.form['idComprador']
                    ped.idVendedor = request.form['idVendedor']
                    ped.idTarjeta = request.form['idTarjeta']
                    ped.fechaRegistro = request.form['fechaRegistro']
                    ped.fechaAtencion = request.form['fechaAtencion']
                    ped.fechaCierre = request.form['fechaCierre']
                    ped.fechaRecepcion = request.form['fechaRecepcion']
                    ped.total = request.form['total']
                    ped.estatus='Pendiente'
                    ped.agregar()
                    flash('¡ Pedido agregado con exito !')
                except:
                    flash('¡ Error al agregar el pedido !')
                return redirect(url_for('consultarPedidos'))
            else:
                abort(404)

        else:
            return redirect(url_for('mostrar_login'))
    except:
        abort(500)


@app.route('/Pedidos/<int:id>')
@login_required
def consultarPedido(id):
    if current_user.is_authenticated:
        ped=Pedidos()
        return render_template('pedidos/editar.html',ped=ped.consultaIndividuall(id))
    else:
        return redirect(url_for('mostrar_login'))


@app.route('/Pedidos/editar',methods=['POST'])
@login_required
def editarPedido():
    if current_user.is_authenticated:
        try:
            ped=Pedidos()
            ped.idPedido = request.form['idPedido']
            ped.idComprador = request.form['idComprador']
            ped.idVendedor = request.form['idVendedor']
            ped.idTarjeta = request.form['idTarjeta']
            ped.fechaRegistro = request.form['fechaRegistro']
            ped.fechaAtencion = request.form['fechaAtencion']
            ped.fechaCierre = request.form['fechaCierre']
            ped.fechaRecepcion = request.form['fechaRecepcion']
            ped.total = request.form['total']
            ped.estatus = request.form['estatus']
            ped.editar()
            flash('¡ Pedido editado con exito !')
        except:
            flash('¡ Error al editar el pedido !')

        return redirect(url_for('consultarPedidos'))
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/Pedidos/eliminar/<int:id>')
@login_required
def eliminarPedido(id):
    if current_user.is_authenticated:
        try:
            ped=Pedidos()
            ped.eliminar(id)
            flash('Pedido eliminado con exito')
        except:
            flash('Error al eliminar el pedido')
        return redirect(url_for('consultarPedidos'))
    else:
        return redirect(url_for('mostrar_login'))

# fin del manejo de pedidos
#manejo de errores
@app.errorhandler(404)
def error_404(e):
    return render_template('comunes/error_404.html'),404

@app.errorhandler(500)
def error_500(e):
    return render_template('comunes/error_500.html'),500

#TARJETAS
@app.route('/TipoPago')
@login_required
def consultarTP():
    if current_user.is_authenticated and current_user.is_admin():
        ti = tipoPago()
        return render_template('/TipoPago/consultaTP.html',tipopago = ti.consultarTP())
    else:
        abort(404)

@app.route('/TipoPago/nueva')
@login_required
def nuevoTP():
    if current_user.is_authenticated and current_user.is_admin():
            return render_template('TipoPago/agregarTP.html')
    else:
        abort(404)

@app.route('/TipoPago/agregar',methods=['post'])
@login_required
def agregarTP():
    try:
        if current_user.is_authenticated:
            if current_user.is_admin():
                try:
                    tar=tipoPago()
                    tar.tipo=request.form['tipo']
                    tar.agregar()
                    flash('¡ Tipo de pago agregado con exito !')
                except:
                    flash('¡ Error al agregar el Tipo de pago !')
                return redirect(url_for('consultarTP'))
            else:
                abort(404)

        else:
            return redirect(url_for('mostrar_login'))
    except:
        abort(500)

@app.route('/TipoPago/editar',methods=['post'])
@login_required
def editarTP():
    if current_user.is_authenticated and current_user.is_admin():
        try:
            ti=tipoPago()
            ti.idTipoPago=request.form['id']
            ti.tipo=request.form['tipo']
            ti.editar()
            flash('¡ Tipo de Pago editado con exito !')
        except:
            flash('¡ Error al editar el Tipo de Pago !')

        return redirect(url_for('consultarTP'))
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/TipoPago/<int:id>')
@login_required
def consultaTP(id):
    if current_user.is_authenticated and current_user.is_admin():
        ti=tipoPago()
        return render_template('TipoPago/editarTP.html',tipopa=ti.consultaIndividuall(id))
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/TipoPago/eliminar/<int:id>')
@login_required
def eliminarTP(id):
    if current_user.is_authenticated and current_user.is_admin():
        try:
            ti=tipoPago()
            ti.eliminar(id)
            flash('Tipo de Pago eliminado con exito')
        except:
            flash('Error al eliminar el Tipo de Pago')
        return redirect(url_for('consultarTP'))
    else:
        return redirect(url_for('mostrar_login'))

#PAQUETERÍAS
@app.route('/Transportes')
def consultaGeneralTransportes():
    t=Transportes()
    return render_template('Transportes/Consultar.html',transportes=t.consultaGeneral())

@app.route('/Transportes/Registrar')
def RegistrarTransporte():
    return render_template('Transportes/Registrar.html')

@app.route('/Transportes/nuevo',methods=['post'])
def nuevoTransporte():
    t = Transportes()
    t.nombre = request.form['nombre']
    t.telefono=request.form['telefono']
    t.estatus = 'A'
    t.agregar()
    flash('Transporte registrado con exito')
    return render_template('Transportes/Registrar.html')

@app.route('/Transportes/<int:id>')
def ConsultaIndTransportes(id):
    t = Transportes()
    return render_template('Transportes/Modificar.html',trans=t.consultaIndividual(id))

@app.route('/Transportes/Modificar',methods=['post'])
def ModificarTransportes():
    t= Transportes()
    t.idTransportes = request.form['Id']
    t.nombre = request.form['nombre']
    t.telefono=request.form['telefono']
    t.estatus = 'A'
    t.editar()
    flash('La modificación del Transporte se realizó con exito')
    return render_template('Transportes/Modificar.html',trans=t)

@app.route('/Transportes/eliminar/<int:id>')
def eliminarTransporte(id):
    t=Transportes()
    t.eliminar(id)
    return render_template('Transportes/Consultar.html', transportes=t.consultaGeneral())

##############################
@app.route('/carrito/agregar/<data>',methods=['get'])
def agregarProductoCarrito(data):
    msg=''
    if current_user.is_authenticated and current_user.is_comprador():
        datos=json.loads(data)
        carrito=Carrito()
        carrito.idProducto=datos['idProducto']
        carrito.idUsuario=current_user.idUsuario
        carrito.cantidad=datos['cantidad']
        carrito.agregarCarrito()
        msg={'estatus':'ok','mensaje':'Producto agregado a la cesta.'}
    else:
        msg = {"estatus": "error", "mensaje": "Debes iniciar sesion"}
    return json.dumps(msg)

@app.route("/carrito")
@login_required
def consultarCesta():
    if current_user.is_authenticated:
        carrito = Carrito()
        return render_template('carrito/consultaGeneral.html',cesta=carrito.consultaGeneralCar(current_user.idUsuario))
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/carrito/consultacarrito/<int:id>')
@login_required
def consultarDeCarrito(id):
    carrito = Carrito()
    if current_user.is_authenticated and current_user.is_comprador():
        return render_template('carrito/editarCarrito.html', carrito=carrito.consultaIndividuall(id))
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/carrito/editar', methods=['POST'])
@login_required
def editarCarrito():
    if current_user.is_authenticated and current_user.is_comprador():
        try:
            car = Carrito()
            car.idCarrito = request.form['idCarrito']
            car.idUsuario = request.form['idUser']
            car.idProducto = request.form['idProd']
            car.fecha = request.form['fecha']
            car.cantidad = request.form['cantidad']
            car.estatus = 'Activo'
            car.editar()
            flash('¡ Carrito editado con exito !')
        except:
            flash('¡ Error al editar el carrito !')
        return redirect(url_for('consultarCesta'))
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/Carrito/eliminar/<int:id>')
@login_required
def eliminarCarrito(id):
    if current_user.is_authenticated and current_user.is_comprador():
        try:
            carrito=Carrito()
            carrito.eliminarProductoDeCarrito(id)
            flash('Elemento del carrito eliminada con exito')
        except:
            flash('Error al eliminar el elemento del carrito')
        return redirect(url_for('consultarCesta'))
    else:
        return redirect(url_for('mostrar_login'))

#DETALLE PEDIDOS

@app.route('/Pedidos/verpedidos/detallespedidos')
@login_required
def consultarDetallePedidos():
   detped=DetallePedidos()
   return render_template('/detallepedidos/consultaGeneral.html',detallepedidos = detped.consultaDetallesPedido())


@app.route('/Pedidos/verpedidos/detallespedidos/nuevo')
@login_required
def nuevoDetallePedidos():
    if current_user.is_authenticated:
            return render_template('detallepedidos/agregar.html')
    else:
        abort(404)

@app.route('/Pedidos/verpedidos/detallespedidos/agregar',methods=['post'])
@login_required
def agregarDetallePedidos():
    try:
        if current_user.is_authenticated:
            if current_user.is_authenticated:
                try:
                    detped=DetallePedidos()
                    detped.idPedido=request.form['idPedido']
                    detped.idProducto=request.form['idProducto']
                    detped.precio=request.form['precio']
                    detped.cantidadPedida=request.form['cantidadPedida']
                    detped.cantidadEnviada = request.form['cantidadEnviada']
                    detped.cantidadAceptada = request.form['cantidadAceptada']
                    detped.cantidadRechazada = request.form['cantidadRechazada']
                    detped.subtotal = request.form['subtotal']
                    detped.estatus='Pendiente'
                    detped.comentario = request.form['comentario']
                    detped.agregar()
                    flash('¡ Detalle agregada con exito !')
                except:
                    flash('¡ Error al agregar el detalle !')
                return redirect(url_for('consultarDetallePedidos'))
            else:
                abort(404)
        else:
            return redirect(url_for('mostrar_login'))
    except:
        abort(500)

@app.route('/Pedidos/verpedidos/detallespedidos/<int:id>')
@login_required
def modDetallePedido(id):
    if current_user.is_authenticated:
        detped=DetallePedidos()
        return render_template('/detallepedidos/editar.html',detped=detped.consultaIndividuall(id))
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/Pedidos/verpedidos/detallespedidos/editar',methods=['POST'])
@login_required
def editarDetallePedidos():
    if current_user.is_authenticated:
        try:
            detped = DetallePedidos()
            detped.idDetalle = request.form['idDetalle']
            detped.idPedido = request.form['idPedido']
            detped.idProducto = request.form['idProducto']
            detped.precio = request.form['precio']
            detped.cantidadPedida = request.form['cantidadPedida']
            detped.cantidadEnviada = request.form['cantidadEnviada']
            detped.cantidadAceptada = request.form['cantidadAceptada']
            detped.cantidadRechazada = request.form['cantidadRechazada']
            detped.subtotal = request.form['subtotal']
            detped.estatus = 'Pendiente'
            detped.comentario = request.form['comentario']
            detped.editar()
            flash('¡ Detalle agregado con exito !')
        except:
            flash('¡ Error al editar el detalle!')

        return redirect(url_for('consultarDetallePedidos'))
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/Pedidos/verpedidos/detallespedidos/eliminar/<int:id>')
@login_required
def eliminarDetallePedido(id):
    if current_user.is_authenticated:
        try:
            detped=DetallePedidos()
            #paq.eliminacionLogica(id)
            detped.eliminar(id)
            flash('DetallePedidos eliminada con exito')
        except:
            flash('Error al eliminar la DetallePedidos')
        return redirect(url_for('consultarDetallePedidos'))
    else:
        return redirect(url_for('mostrar_login'))


##################CLIENTES

@app.route('/Clientes')
def ConsultaGeneralClientes():
    cli=Clientes()
    clientes=cli.consultaGeneral()
    return render_template('Clientes/Consultar.html',clientes=clientes)

@app.route('/Clientes/Registrar')
def RegistrarCliente():
    return render_template('Clientes/Registrar.html')


@app.route('/Clientes/nuevo',methods=['post'])
@login_required
def RegistroCliente():
    cli= Clientes()
    cli.nombre = request.form['nombre']
    cli.direccion = request.form['direccion']
    cli.telefono = request.form['telefono']
    cli.RFC = request.form['RFC']
    cli.insertar()
    flash('Cliente registrado con exito')
    return render_template('Clientes/Registrar.html')

@app.route('/Clientes/Ver/<int:id>')
def ConsultaIndClientes(id):
    cli = Clientes()
    return render_template('Clientes/Modificar.html',client=cli.consultaIndividual(id))

@app.route('/Clientes/Modificar',methods=['post'])
def ModificacionClientes():
    cli=Clientes()
    cli.idCliente = request.form['idCliente']
    cli.nombre = request.form['nombre']
    cli.direccion = request.form['direccion']
    cli.telefono = request.form['telefono']
    cli.RFC = request.form['RFC']
    cli.actualizar()
    flash('La modificación del Cliente se realizó con exito')
    return render_template('Clientes/Modificar.html',client=cli)

@app.route('/Clientes/eliminar/<int:id>')
def eliminarCliente(id):
    cli=Clientes()
    cli.eliminar(id)
    return render_template('Clientes/Consultar.html',clientes=cli.consultaGeneral())
#################################

if __name__=='__main__':
    db.init_app(app)#Inicializar la BD - pasar la configuración de la url de la BD
    app.run(debug=True)



