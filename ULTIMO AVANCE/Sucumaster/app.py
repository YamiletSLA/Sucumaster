from datetime import timedelta
from urllib import request

from flask import Flask,render_template,request,redirect,url_for,flash,session,abort, make_response
from flask_bootstrap import Bootstrap
from modelo.Dao import db, Categoria, Producto, Usuario, tipoPago, Transportes, Ventas, detalleVenta, Clientes, Especiales, Estante
from flask_login import login_required,login_user,logout_user,current_user,LoginManager
import json
import pdfkit

import os
import pdfkit
from jinja2 import Environment, FileSystemLoader
ruta= os.path.join(os.getcwd())

app = Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:root@localhost/sucumaster'
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://userSucuMaster:hola.123@localhost:3306/sucumaster'
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:root@127.0.0.1:3306/sucumaster'
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:root@localhost:3306/sucumaster'
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
        usuario.contraseña=request.form['password']
        usuario.tipoUsuario = request.form['tipoUsuario']
       ## usuario.tipoUsuario = request.values.get("tipo", "Vendedor")
        usuario.estatus = 'A'
        usuario.agregar()
        flash('¡ Usuario registrado con exito')
    except:
        flash('¡ Error al agregar al usuario !')
    return render_template('usuarios/registrarCuenta.html')


@app.route('/Usuarios/eliminar/<int:id>')
def eliminarUsuario(id):
    usu=Usuario()
    usu.eliminar(id)
    return render_template('principal.html',usuario=usu.consultaUsuarios())


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

@app.route('/Usuarios/Almacenista')
@login_required
def consultarAlmacenista():
    if current_user.is_authenticated and current_user.is_admin():
        us=Usuario()
        return render_template('usuarios/Almacenista.html',usuario=us.consultaUsuarios())
    else:
        return render_template('usuarios/login.html')
@app.route('/Usuarios/Vendedores')
@login_required
def consultarVendedores():
    if current_user.is_authenticated and current_user.is_admin():
        user=Usuario()
        return render_template('usuarios/vendedores.html',usuario=user.consultaUsuarios())
    else:
        return render_template('usuarios/login.html')
@app.route('/Usuarios/Admin')
@login_required
def consultarAdmin():
    if current_user.is_authenticated and current_user.is_admin():
        user=Usuario()
        return render_template('usuarios/admins.html',usuario=user.consultaUsuarios())
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
            user.nombreUsuario=request.form['nombreUsuario']
            user.tipoUsuario=request.form['tipoUsuario']
            user.estatus= request.form['estatus']
            user.editarUsua()
            flash('¡ Usuario editado con exito !')
        except:
            flash('¡ Error al editar el usuario !')

        if user.tipoUsuario == 'Almacenista':
            return redirect(url_for('consultarAlmacenista'))
        else:
            if user.tipoUsuario == 'Vendedor':
                return redirect(url_for('consultarVendedores'))
            else:
                return redirect(url_for('consultarAdmin'))

    else:
        return redirect(url_for('mostrar_login'))

######



######
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
        prod_dic={'idProducto':prod.idProducto,'nombre':prod.nombre,'descripcion':prod.descripcion,'precio':prod.precio,'existencia':prod.existencia}
        listaProductos.append(prod_dic)
    #print(listaProductos)
    var_json=json.dumps(listaProductos)
    return var_json

@app.route('/producto/<int:id>')
def consultarProducto(id):
    if current_user.is_authenticated and  current_user.is_admin() or current_user.is_vendedor():
        prod = Producto()
        prod = prod.consultaIndividual(id)
        dict_producto = {"idProducto": prod.idProducto, "nombre": prod.nombre, "descripcion": prod.descripcion,
                         "precio": prod.precio, "existencia": prod.existencia}
        return json.dumps(dict_producto)
    else:
        msg = {"estatus": "error", "mensaje": "Debes iniciar sesion"}
        return json.dumps(msg)

@app.route('/producto/ver/<int:id>')
def consultarProd(id):
    if current_user.is_authenticated:
        prod=Producto()
        return render_template('productos/editarP.html', prod=prod.consultaIndividual(id))
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/Productos/nuevo')
@login_required
def nuevoProducto():
    if current_user.is_authenticated and current_user.is_admin() or current_user.is_almacenista():
            return render_template('productos/agregarP.html')
    else:
        abort(404)

@app.route('/Productos/agregar',methods=['post'])
@login_required
def agregarProducto():
    try:
        if current_user.is_authenticated:
            if current_user.is_admin() or current_user.is_almacenista():
                try:
                    prod=Producto()
                    prod.idCategorias=request.form['categoria']
                    prod.nombre=request.form['nombre']
                    prod.descripcion=request.form['desc']
                    prod.existencia = request.form['exist']
                    prod.precio=request.form['precio']
                    prod.estatus = 'Activo'
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
    if current_user.is_authenticated and current_user.is_admin() or current_user.is_almacenista():
       try:
            prod=Producto()
            prod.idCategorias=request.form['idCategorias']
            prod.nombre=request.form['nombre']
            prod.descripcion = request.form['desc']
            prod.existencia = request.form['exist']
            prod.precio = request.form['precio']
            prod.estatus = request.form['estatus']
            prod.estatus = request.values.get("estatus", "Inactivo")
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
    if current_user.is_authenticated and current_user.is_admin() or current_user.is_almacenista():
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
    if current_user.is_authenticated and current_user.is_admin() or current_user.is_almacenista():
            return render_template('categorias/agregar.html')
    else:
        abort(404)

@app.route('/Categorias/agregar',methods=['post'])
@login_required
def agregarCategoria():
    try:
        if current_user.is_authenticated:
            if current_user.is_admin() or current_user.is_almacenista():
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
    if current_user.is_authenticated:
        cat=Categoria()
        return render_template('categorias/editar.html',cat=cat.consultaIndividual(id))
    else:
        return redirect(url_for('mostrar_login'))


@app.route('/Categorias/editar',methods=['POST'])
@login_required
def editarCategoria():
    if current_user.is_authenticated and current_user.is_admin() or current_user.is_almacenista:
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
    ped=detalleVenta()
    return render_template('pedidos/consultaGeneral.html',pedidos=ped.consultaGeneralDV())

@app.route('/Pedidos/agregar',methods=['post'])
@login_required
def agregarPedidos():
    try:
        if current_user.is_authenticated:
            if current_user.is_authenticated:
                try:
                    ped=detalleVenta()
                    ped.idUsuario=request.form['idUsuario']
                    ped.idVentas = request.form['idVentas']
                    ped.fechaRegistro = request.form['fechaRegistro']
                    ped.fechaRecepcion = request.form['fechaRecepción']
                    ped.fechaCierre = request.form['fechaCierre']
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
        ped=detalleVenta()
        return render_template('pedidos/editar.html',ped=ped.consultaIndividuall(id))
    else:
        return redirect(url_for('mostrar_login'))


@app.route('/Pedidos/editar',methods=['POST'])
@login_required
def editarPedido():
    if current_user.is_authenticated:
        try:
            ped=detalleVenta()
            ped.idPedido = request.form['idPedido']
            ped.idUsuario = request.form['idUsuario']
            ped.idVentas = request.form['idVentas']
            ped.fechaRegistro = request.form['fechaRegistro']
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
            ped=detalleVenta()
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
    if current_user.is_authenticated and current_user.is_admin() or current_user.is_vendedor:
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
@app.route('/Venta/agregar/<data>',methods=['get'])
def agregarProductoVenta(data):
    msg=''
    if current_user.is_authenticated and current_user.is_admin() or current_user.is_vendedor():
        datos=json.loads(data)
        v=Ventas()
        v.idProducto=datos['idProducto']
        v.idUsuario=current_user.idUsuario
        v.cantidad=datos['cantidad']
        v.total=datos['total']
        v.agregarVenta()
        msg={'estatus':'ok','mensaje':'Producto agregado a la venta.'}
    else:
        msg = {"estatus": "error", "mensaje": "Debes iniciar sesion"}
    return json.dumps(msg)

@app.route("/Venta")
@login_required
def consultarVenta():
    if current_user.is_authenticated:
        v = Ventas()
        return render_template('Ventas/consultaGeneral.html',venta=v.consultaGeneral())
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/Venta/consultaventa/<int:id>')
@login_required
def consultaVenta(id):
    v = Ventas()
    if current_user.is_authenticated and current_user.is_admin() or current_user.is_vendedor():
        return render_template('Ventas/editarV.html', ventas=v.consultaIndividuall(id))
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/Venta/editar', methods=['POST'])
@login_required
def editarVenta():
    if current_user.is_authenticated and current_user.is_admin() or current_user.is_vendedor():
        try:
            car = Ventas()
            car.idVentas = request.form['id']
            car.idUsuario = request.form['idUser']
            car.idProducto = request.form['idProd']
            car.fecha = request.form['fecha']
            car.cantidad = request.form['cantidad']
            car.estatus = 'Activo'
            car.editar()
            flash('¡ Carrito editado con exito !')
        except:
            flash('¡ Error al editar el Ventas !')
        return redirect(url_for('consultarVenta'))
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/Venta/eliminar/<int:id>')
@login_required
def eliminarCarrito(id):
    if current_user.is_authenticated and current_user.is_vendedor() or current_user.is_admin():
        try:
            carrito=Ventas()
            carrito.eliminarProductoDeVenta(id)
            flash('Elemento del Ventas eliminada con exito')
        except:
            flash('Error al eliminar el elemento del Ventas')
        return redirect(url_for('consultarVenta'))
    else:
        return redirect(url_for('mostrar_login'))

#DETALLE PEDIDOS

@app.route('/Pedidos/verpedidos/detallespedidos')
@login_required
def consultarDetallePedidos():
   detped=detalleVenta()
   return render_template('/detallepedidos/consultaGeneral.html',detallepedidos = detped.consultaDV())


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
                    detped=detalleVenta()
                    detped.idDetalleVenta=request.form['idDetalleVenta']
                    detped.idUsuario=request.form['idUsuario']
                    detped.idVentas=request.form['idVentas']
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
        detped=detalleVenta()
        return render_template('/detallepedidos/editar.html',detped=detped.consultaIndividuall(id))
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/Pedidos/verpedidos/detallespedidos/editar',methods=['POST'])
@login_required
def editarDetallePedidos():
    if current_user.is_authenticated:
        try:
            detped = detalleVenta()
            detped.idDetalleVenta = request.form['idDetalleVenta']
            detped.idVentas = request.form['idVentas']
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
            detped=detalleVenta()
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

##################ESPECIALES

@app.route('/Especiales')
def ConsultaGeneralEspeciales():
    esp=Especiales()
    especiales=esp.consultaGeneral()
    return render_template('Especiales/Consultar.html',especiales=especiales)

@app.route('/Especiales/Registrar')
def RegistrarEspeciales():
    return render_template('Especiales/Registrar.html')


@app.route('/Especiales/nuevo',methods=['post'])
@login_required
def RegistroEspeciales():
    esp= Especiales()
    esp.nombre = request.form['nombre']
    esp.descripcion = request.form['descripcion']
    esp.costo = request.form['costo']
    esp.existencia = request.form['existencia']
    esp.insertar()
    flash('Especial registrado con exito')
    return render_template('Especiales/Registrar.html')

@app.route('/Especiales/Ver/<int:id>')
def ConsultaIndEspeciales(id):
    esp = Especiales()
    return render_template('Especiales/Modificar.html',especial=esp.consultaIndividual(id))

@app.route('/Especiales/Modificar',methods=['post'])
def ModificacionEspeciales():
    esp=Especiales()
    esp.idEspeciales = request.form['idEspeciales']
    esp.nombre = request.form['nombre']
    esp.descripcion = request.form['descripcion']
    esp.costo = request.form['costo']
    esp.existencia = request.form['existencia']
    esp.actualizar()
    flash('La modificación de especiales se realizó con exito')
    return render_template('Especiales/Modificar.html',especial=esp)

@app.route('/Especiales/eliminar/<int:id>')
def eliminarEspeciales(id):
    esp=Especiales()
    esp.eliminar(id)
    return render_template('Especiales/Consultar.html',especiales=esp.consultaGeneral())

##Estante
@app.route('/Estante')
def consultaGeneralEstante():
    e=Estante()
    return render_template('Estante/Consultar.html',estante=e.consultaGeneral())

@app.route('/Estante/Registrar')
def RegistrarEstante():
    return render_template('Estante/Registrar.html')

@app.route('/Estante/nuevo',methods=['post'])
def nuevoEstante():
    e = Estante()
    e.nombre = request.form['nombre']
    e.ubicacion=request.form['ubicacion']
    e.agregar()
    flash('Estante registrado con exito')
    return render_template('Estante/Registrar.html')

@app.route('/Estante/<int:id>')
def ConsultaIndEstante(id):
    e = Estante()
    return render_template('Estante/Modificar.html',est=e.consultaIndividual(id))

@app.route('/Estante/Modificar',methods=['post'])
def ModificarEstante():
    e= Estante()
    e.idEstante = request.form['Id']
    e.nombre = request.form['nombre']
    e.ubicacion=request.form['ubicacion']
    e.editar()
    flash('La modificación del estante se realizó con exito')
    return render_template('Estante/Modificar.html',est=e)

@app.route('/Estante/eliminar/<int:id>')
def eliminarEstante(id):
    e=Estante()
    e.eliminar(id)
    return render_template('Estante/Consultar.html', estantes=e.consultaGeneral())
##############pdf
@app.route('/docNominas/<int:id>')
def docNominas(id):
    env = Environment(loader=FileSystemLoader("/templates"))
    template = env.get_template("/docs/Recibo.html")
    v = Ventas()
    v = v.consultaIndividual(id)

    datos={
        'ventas': v

    }
    html = template.render(datos)
    file = open(ruta + '/static/docs/Formato-NominaTMP.html', "w")
    file.write(html)
    file.close()
    pdfkit.from_file(ruta + '\static\docs\Formato-NominaTMP.html', ruta + '\static\docs\Formato-Nomina.pdf')
    pdf = open(ruta + '\static\docs\Formato-Nomina.pdf', "rb")
    doc = pdf.read()
    pdf.close()
    # os.remove(ruta + '\static\docs\Formato-NominaTMP.html')
    # os.remove(ruta+'\Static\docs\Formato-Nomina.pdf')
    return doc
if __name__=='__main__':
    db.init_app(app)#Inicializar la BD - pasar la configuración de la url de la BD
    app.run(debug=True)



