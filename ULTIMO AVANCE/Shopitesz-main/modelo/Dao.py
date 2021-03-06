from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column,Integer,String,BLOB,ForeignKey,Float, Date
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
import datetime
db=SQLAlchemy()

class Categoria(db.Model):
    __tablename__='Categorias'
    idCategorias=Column(Integer,primary_key=True)
    nombre=Column(String,unique=True)

    def consultaGeneral(self):
        return self.query.all()
        #return self.query.filter(Categoria.estatus=='Activa').all()

    def consultaIndividual(self,id):
        return Categoria.query.get(id)

    def agregar(self):
        db.session.add(self)
        db.session.commit()

    def editar(self):
        db.session.merge(self)
        db.session.commit()

    def eliminar(self,id):
        cat=self.consultaIndividual(id)
        db.session.delete(cat)
        db.session.commit()

class Producto(db.Model):
    __tablename__='Productos'
    idProducto=Column(Integer,primary_key=True)
    idCategorias=Column(Integer,ForeignKey('Categorias.idCategorias'))
    nombre=Column(String,nullable=False)
    descripcion=Column(String,nullable=True)
    precio=Column(Float,nullable=False)
    existencia = Column(Integer, nullable=False)
    estatus=Column(String, nullable=False)
    categoria=relationship('Categoria',backref='productos',lazy='select')


    def consultaGeneral(self):
        return self.query.filter(Producto.estatus == 'Activo').all()

    def consultarProductosPorCategoria(self, idCategorias):
        return self.query.filter(Producto.idCategorias == idCategorias, Producto.estatus == 'Activo').all()

    def consultaIndividual(self,id):
        return Producto.query.get(id)

    def agregar(self):
        db.session.add(self)
        db.session.commit()

    def eliminar(self,id):
        prod=self.consultaIndividual(id)
        db.session.delete(prod)
        db.session.commit()

    def editar(self):
        db.session.merge(self)
        db.session.commit()

    def eliminacionLogica(self, id):
        tar = self.consultaIndividual(id)
        tar.estatus = 'Inactivo'
        tar.editar()


class Usuario(UserMixin,db.Model):
    __tablename__='usuario'
    idUsuario=Column(Integer,primary_key=True)
    nombreCompleto=Column(String,nullable=False)
    nombreUsuario=Column(String,nullable=False)
    contrase??a=Column(String(128),nullable=False)
    estatus = Column(String, nullable=False)
    tipoUsuario=Column(String,nullable=False)


    # @property #Implementa el metodo Get (para acceder a un valor)
    # def password(self):
    #     raise AttributeError('El password no tiene acceso de lectura')
    #
    # @password.setter #Definir el metodo set para el atributo password_hash
    # def password(self,password):#Se informa el password en formato plano para hacer el cifrado
    #     self.contrase??a=generate_password_hash(password)

    def validarPassword(self,password):
        return check_password_hash(self.contrase??a,password)

    def isValid(self,nomUsu,password):
        usuario = Usuario.query.filter(Usuario.nombreUsuario == nomUsu).first()
        if usuario != None and usuario.validarPassword(password) and usuario.is_active():
            return usuario
        else:
            return None
    #Definici??n de los m??todos para el perfilamiento
    def is_authenticated(self):
        return True

    def is_active(self):
        if self.estatus=='A':
            return True
        else:
            return False
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.idUsuario

    def is_admin(self):
        if self.tipoUsuario=='Administrador':
            return True
        else:
            return False
    def is_vendedor(self):
        if self.tipoUsuario=='Vendedor':
            return True
        else:
            return False
    def is_almecenista(self):
        if self.tipoUsuario=='Almacenista':
            return True
        else:
            return False
    #Definir el m??todo para la autenticacion
    def validar(self,nomUsu,password):
        usuario = Usuario.query.filter(Usuario.nombreUsuario == nomUsu, Usuario.contrase??a == password).first()
        if usuario != None and usuario.is_active():
            return usuario
        else:
            return None
    #M??todo para agregar una cuenta de usuario
    def agregar(self):
        db.session.add(self)
        db.session.commit()

    def consultaUsuarios(self):
        return self.query.all()

    def consultaIndividual(self,id):
        return self.query.get(id)

    #M??todo para editar un usuario
    def editarUsua(self):
        db.session.merge(self)
        db.session.commit()

    def eliminacionLogica(self,id):
        usuario = self.consultaIndividual(id)
        usuario.estatus = 'I'
        usuario.editarUsua()

    def eliminar(self,id):
        usuario=self.consultaIndividual(id)
        db.session.delete(usuario)
        db.session.commit()








class detalleVenta(db.Model):
    __tablename__='DetalleVenta'
    idPedido=Column(Integer,primary_key=True)
    idUsuario = Column(Integer, ForeignKey('usuario.idUsuario'))
    idVentas = Column(Integer, ForeignKey('ventas.idVentas'))
    fechaRegistro = Column(Date,default=datetime.date.today())
    fechaRecepcion = Column(String, nullable=False)
    fechaCierre = Column(Date)
    total = Column(Float, nullable=False)
    estatus = Column(String, nullable=False)

    def consultaGeneral(self):
        return self.query.all()
        #return self.query.filter(Categoria.estatus=='Activa').all()

    def consultaIndividuall(self,id):
        return detalleVenta.query.get(id)

    def agregar(self):
        db.session.add(self)
        db.session.commit()

    def editar(self):
        db.session.merge(self)
        db.session.commit()

    def eliminar(self,id):
        ped=self.consultaIndividuall(id)
        db.session.delete(ped)
        db.session.commit()

    def eliminacionLogica(self,id):
        ped = self.consultaIndividuall(id)
        ped.estatus='Cancelado'
        ped.editar()

class tipoPago(db.Model):
    __tablename__='TipoPago'
    idTipoPago=Column(Integer,primary_key=True)
    tipo=Column(String, nullable=False)

    def consultarTP(self):
        return self.query.all()

    def agregar(self):
        db.session.add(self)
        db.session.commit()

    def editar(self):
        db.session.merge(self)
        db.session.commit()

    def consultaIndividuall(self,id):
        return tipoPago.query.get(id)

    def eliminar(self,id):
        cat=self.consultaIndividuall(id)
        db.session.delete(cat)
        db.session.commit()


class Transportes(db.Model):
    __tablename__ = 'Transportes'
    idTransportes = Column(Integer, primary_key=True)
    nombre = Column(String(20))
    telefono=Column(String(10))
    estatus=Column(String(1))

    def consultaGeneral(self):
        return self.query.all()

    def agregar(self):
        db.session.add(self)
        db.session.commit()

    def editar(self):
        db.session.merge(self)
        db.session.commit()

    def consultaIndividual(self,id):
        return Transportes.query.get(id)

    def eliminar(self,id):
        paq=self.consultaIndividual(id)
        db.session.delete(paq)
        db.session.commit()

    def eliminacionLogica(self,id):
        paq = self.consultaIndividual(id)
        paq.estatus='Inactiva'
        paq.editar()

class Ventas(db.Model):
    __tablename__='ventas'
    idVentas=Column(Integer,primary_key=True)
    idUsuario=Column(Integer,ForeignKey('usuario.idUsuario'))
    idProducto=Column(Integer,ForeignKey('Productos.idProducto'))
    fecha=Column(Date,default=datetime.date.today())
    cantidad=Column(Integer,nullable=False,default=1)
    estatus=Column(String,nullable=False,default='Pendiente')
    producto=relationship('Producto',backref='ventas',lazy='select')
    usuario=relationship('Usuario',backref='ventas',lazy='select')

    def agregarVenta(self):
        db.session.add(self)
        db.session.commit()

    def consultaGeneral(self):
        return self.query.all()

    def consultaIndividuall(self,id):
        return Ventas.query.get(id)

    def eliminarProductoDeVenta(self,id):
        venta=self.consultaIndividuall(id)
        db.session.delete(venta)
        db.session.commit()

    def editar(self):
        db.session.merge(self)
        db.session.commit()

class DetallePedidos(db.Model):
    __tablename__='detallepedidos'
    idDetalle=Column(Integer,primary_key=True)
    idPedido=Column(Integer,ForeignKey('Pedidos.idPedido'))
    idProducto = Column(Integer, ForeignKey('Productos.idProducto'))
    precio = Column(Float, nullable=False)
    cantidadPedida=Column(Integer, nullable=False)
    cantidadEnviada=Column(Integer, nullable=False)
    cantidadAceptada = Column(Integer, nullable=False)
    cantidadRechazada = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)
    estatus=Column(String, nullable=False)
    comentario = Column(String, nullable=False)
    producto = relationship('Producto',backref='DetallePedidos',lazy='select')

    def consultaDetallesPedido(self):
        return self.query.all()

    def agregar(self):
        db.session.add(self)
        db.session.commit()

    def editar(self):
        db.session.merge(self)
        db.session.commit()

    def consultaIndividuall(self,id):
        return DetallePedidos.query.get(id)

    def eliminar(self,id):
        detped=self.consultaIndividuall(id)
        db.session.delete(detped)
        db.session.commit()

    def eliminacionLogica(self,id):
        paq = self.consultaIndividuall(id)
        paq.estatus='Cancelado'
        paq.editar()

######CLIENTES
##################Clientes
class Clientes(db.Model):
    __tablename__ = 'cliente'
    idCliente = Column(Integer, primary_key=True)
    nombre = Column(String(30))
    direccion = Column(String(45))
    telefono = Column(String(10))
    RFC = Column(String(13))

    def insertar(self):
        db.session.add(self)
        db.session.commit()

    def consultaIndividual(self, id):
        return self.query.get(id)

    def eliminar(self, id):
        obj = self.consultaIndividual(id)
        db.session.delete(obj)
        db.session.commit()

    def actualizar(self):
        db.session.merge(self)
        db.session.commit()

    def consultaGeneral(self):
        return self.query.all()
    # def consultaGeneral(self, pagina):
    #     return self.query.order_by(Transportes.idTransportes.asc()).paginate(pagina, per_page=5, error_out=False).items
    #     # return self.query.all()

    def eliminacionLogica(self,id):
        usuario = self.consultaIndividual(id)
        usuario.estatus = 'I'
        usuario.editar()

##################Especiales
class Especiales(db.Model):
    __tablename__ = 'especiales'
    idEspeciales = Column(Integer, primary_key=True)
    nombre = Column(String(30))
    descripcion = Column(String(20))
    costo = Column(Integer)
    existencia = Column(Integer)

    def insertar(self):
        db.session.add(self)
        db.session.commit()

    def consultaIndividual(self, id):
        return self.query.get(id)

    def eliminar(self, id):
        obj = self.consultaIndividual(id)
        db.session.delete(obj)
        db.session.commit()

    def actualizar(self):
        db.session.merge(self)
        db.session.commit()

    def consultaGeneral(self):
        return self.query.all()
    # def consultaGeneral(self, pagina):
    #     return self.query.order_by(Transportes.idTransportes.asc()).paginate(pagina, per_page=5, error_out=False).items
    #     # return self.query.all()

class Estante(db.Model):
    __tablename__ = 'Estante'
    idEstante = Column(Integer, primary_key=True)
    nombre = Column(String(3))
    ubicacion=Column(String(3))

    def consultaGeneral(self):
        return self.query.all()

    def agregar(self):
        db.session.add(self)
        db.session.commit()

    def editar(self):
        db.session.merge(self)
        db.session.commit()

    def consultaIndividual(self,id):
        return Estante.query.get(id)

    def eliminar(self,id):
        paq=self.consultaIndividual(id)
        db.session.delete(paq)
        db.session.commit()

    def eliminacionLogica(self,id):
        paq = self.consultaIndividual(id)
        paq.estatus='Inactiva'
        paq.editar()

class Almacen(db.Model):
    __tablename__='almacen'
    idAlmacen = Column(Integer, primary_key=True)
    cantProducto = Column(Integer,nullable=False)
    Categoria = Column(String, nullable=False)
    Estante = Column(String, nullable=False)

    def agregar(self):
        db.session.add(self)
        db.session.commit()

    def consultaIndividual(self,id):
        return self.query.get(id)

    def editar(self):
        db.session.merge(self)
        db.session.commit()

    def eliminar(self,id):
        obj = self.consultaIndividual(id)
        db.session.delete(obj)
        db.session.commit()

    def actualizar(self):
        db.session.merge(self)
        db.session.commit()

    def consultaGeneral(self):
        return self.query.all()