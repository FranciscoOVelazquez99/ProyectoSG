from flask import Flask, render_template, url_for, redirect, abort, request, flash, session,send_from_directory, jsonify
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from functools import wraps
from wtforms import StringField, PasswordField, SelectField , SubmitField
from wtforms.validators import InputRequired, Length, DataRequired
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, Text, Time, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker,declarative_base
import os
import json   
from sqlalchemy.dialects.mysql import INTEGER
from datetime import datetime, time


app = Flask(__name__)


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','jfif','webp'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'eQ9xv;ZyR#M@H8@'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'




# Crear una instancia base para las clases de las tablas
Base = declarative_base()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
   
    IDuser = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False, unique=True)
    userpass = Column(String(255), nullable=False)
    userclass = Column(String(255), nullable=False)
    useravatar = Column(String(255), nullable=True)
    def get_id(self):
        return str(self.IDuser)
    
    def has_role(self, role):
        return self.userclass == role
    
    __table_args__ = (
        CheckConstraint('length(userpass) >= 8', name='userpass_check'),
    )


# Definir las clases que representan las tablas
class Category(db.Model):
    __tablename__ = 'category'
   
    IDcategory = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

class Element(db.Model):
    __tablename__ = 'elements'
   
    IDelement = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    disp = db.Column(db.Boolean, nullable=True)
    cantotal = Column(Integer, nullable=False)
    candisp = Column(INTEGER(unsigned=True), nullable=False)
    adds = Column(String(255), nullable=True)
    img = Column(String(255), nullable=True)

class ElementCategory(db.Model):
    __tablename__ = 'elm_category'
   
    id = Column(Integer, primary_key=True, autoincrement=True)
    IDcategory = Column(Integer, ForeignKey('category.IDcategory'))
    IDelement = Column(Integer, ForeignKey('elements.IDelement'))

class Email(db.Model):
    __tablename__ = 'email'
   
    IDemail = Column(Integer, primary_key=True, autoincrement=True)
    IDuser = Column(Integer, ForeignKey('user.IDuser'), nullable=False) 
    address = Column(String(45), nullable=False)

    User = db.relationship('User', backref='email')


class Maintenance(db.Model):
    __tablename__ = 'maintenance'
   
    IDmaintenance = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    details = Column(String(255), nullable=True)
    repeat = db.Column(db.Boolean, nullable=True)
    state = Column(String(255), nullable=False)

class MaintenanceElement(db.Model):
    __tablename__ = 'maintenance_elm'
    id = Column(Integer, primary_key=True, autoincrement=True)
    IDmaintenance = Column(Integer, ForeignKey('maintenance.IDmaintenance'))
    IDelement = Column(Integer, ForeignKey('elements.IDelement'))
    revised = Column(Integer, nullable=True)
    details = Column(String(255), nullable=True)

class Order(db.Model):
    __tablename__ = 'orders'
   
    IDorder = Column(Integer, primary_key=True, autoincrement=True)
    IDuser = Column(Integer, ForeignKey('user.IDuser'))
    time = Column(Time, nullable=False)
    date = Column(Date, nullable=False)
    location = Column(Integer, ForeignKey('location.id'))  # FK con Location
    finish = Column(Date, nullable=True)
    state = Column(String(255), nullable=False)

    # Relación con la tabla Location
    location_info = db.relationship('Location', backref='orders')
    User = db.relationship('User', backref='orders')
    
    # Relación con la tabla OrderElement (para obtener los elementos en la orden)
    order_elements = db.relationship('OrderElement', backref='order')

class OrderElement(db.Model):
    __tablename__ = 'orders_elm'

    id = Column(Integer, primary_key=True, autoincrement=True)
    IDorder = Column(Integer, ForeignKey('orders.IDorder'))
    IDelement = Column(Integer, ForeignKey('elements.IDelement'))
    cant = Column(Integer, nullable=False)

    # Relación con la tabla Element
    element = db.relationship('Element', backref='order_elements')


class OrderRep(db.Model):
    __tablename__ = 'orders_rep'

    id = Column(Integer, primary_key=True, autoincrement=True)
    IDorder = Column(Integer, ForeignKey('orders.IDorder'))
    repeat_day = Column(String(255))

class Location(db.Model):
    __tablename__ = 'location'
   
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    planta = Column(String(255), nullable=True)
    descrip = Column(String(255), nullable=True)
    img = Column(String(255), nullable=True)


class Task(db.Model):
    __tablename__ = 'tareas'
   
    IDtarea = Column(Integer, primary_key=True, autoincrement=True)
    IDorder = Column(Integer, ForeignKey('orders.IDorder'), nullable=True)
    titulo = Column(String(255), nullable=False)
    cuerpo = Column(String(255), nullable=True)
    fecha_in = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=False)
    prioridad = Column(String(255), nullable=True)
    estado = Column(String(255), nullable=True)

with app.app_context():
    # Now you can perform operations like creating tables
    db.create_all() 

# Crear una base de datos SQLite
engine = create_engine('sqlite:///database.db')


# Crear una sesión
Session = sessionmaker(bind=engine)
session = Session()

######## formulario de registro ##########

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Usuario"})
    
    email = StringField(validators=[
                            Length(max=45)], render_kw={"placeholder": "Email"})

    password = PasswordField(validators=[
                            InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Contraseña"})
    
    
    rol = SelectField('Roles', choices=[('ADMIN'), ('LVL1'), ('LVL2'), ('LVL3'), ('LVL4')], default='LVL1')

    submit = SubmitField('Registrar')


class EditForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Usuario"})
    email = StringField(validators=[
                            Length(max=45)], render_kw={"placeholder": "Email"})
    
    password = PasswordField(validators=[
                            Length(min=8, max=20)], render_kw={"placeholder": "Contraseña"})
    
    rol = SelectField('Roles', choices=[('Seleccione un rol'),('ADMIN'), ('LVL1'), ('LVL2'), ('LVL3'), ('LVL4')], default='Seleccione un rol')

    submit = SubmitField('Editar')

###
######## formulario de inicio de sesion ##########

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Usuario"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Contraseña"})

    submit = SubmitField('iniciar sesión')

###

def create_admin():
    with app.app_context(): 
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', userpass=bcrypt.generate_password_hash('admin12345678'),userclass='ADMIN')
            db.session.add(admin)
            db.session.commit()

create_admin()

@login_manager.user_loader
def load_user(IDuser):
    return User.query.get(int(IDuser))

def validate_username(username):
    existing_user_username = User.query.filter_by(
        username=username.data).first()
    if existing_user_username:
        return True

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.userclass in roles:
                abort(403)  # Forbidden access
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_email(email):
    existing_user_email = Email.query.filter_by(
        address=email.data).first()
    if existing_user_email:
        return True

def ramdom_string_img(filename):
    import random
    import string
    
    # Obtener el nombre y la extensión del archivo
    nombre, extension = os.path.splitext(filename)
    
    # Generar una cadena aleatoria de 6 dígitos
    cadena_aleatoria = ''.join(random.choices(string.digits, k=6))
    
    # Combinar el nombre original, la cadena aleatoria y la extensión
    nuevo_nombre = f"{nombre}_{cadena_aleatoria}{extension}"
    
    return nuevo_nombre

############################ Login ###################################################
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route("/inicio", methods=['GET', 'POST'])
@login_required
def inicio():
    return render_template('inicio.html')

@app.route("/pedidos", methods=['GET', 'POST'])
@login_required
def pedidos():
    return render_template('PEDIDOS/pedidos.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.userclass != 'LVL1':
                if bcrypt.check_password_hash(user.userpass, form.password.data):
                    login_user(user)
                    return redirect(url_for('inicio'))
            if user.userclass == 'LVL1' or 'LVL2':
                if bcrypt.check_password_hash(user.userpass, form.password.data):
                    login_user(user)
                    return redirect(url_for('pedidos'))
    return render_template('INICIO-SESION/index.html', form=form)



@app.route('/static/')
def serve_static(path):
    return send_from_directory(
        app.config['static'],path, as_attachment=True
  )
############################ //////// ###################################################

############################ Loginout ###################################################

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

############################ //////// ###################################################





############################ funciones de ADMIN ###################################################

########### registro #########
@ app.route('/registro', methods=['GET', 'POST'])
@login_required
@roles_required('ADMIN')
def registro():
    form = RegisterForm()
    formedit = EditForm()
    users = User.query.join(Email,User.IDuser==Email.IDuser).all()
    if form.validate_on_submit():
        if validate_username(form.username):
            flash('El usuario ya existe.', 'warning')
            return redirect(url_for('registro'))  
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, userpass=hashed_password,userclass=form.rol.data)
        db.session.add(new_user)
        if form.email.data:
            userid = User.query.filter(
                User.username == form.username.data
            ).first()

            new_mail= Email(IDuser= userid.IDuser,address=form.email.data)
            db.session.add(new_mail)
            pass
        db.session.commit()
        flash('Usuario creado.', 'success')
        return redirect(url_for('registro'))
    return render_template('REGISTRO/index.html', users=users,form=form,formedit=formedit)


@app.route('/editar_usuario/<int:user_id>', methods=['POST'])
@login_required
@roles_required('ADMIN')
def editar_usuario(user_id):
    formedit = EditForm()
    user = User.query.get_or_404(user_id)
    if formedit:
        user.username = formedit.username.data
        if formedit.password.data:
            user.userpass = bcrypt.generate_password_hash(formedit.password.data)
        if formedit.rol.data != 'Seleccione un rol':
            user.userclass = formedit.rol.data
        db.session.commit()
        flash('Usuario editado exitosamente!', 'success')

        if formedit.email.data:
            user.email.address = formedit.email.data
            db.session.commit()
        return redirect(url_for('registro'))
    return redirect(url_for('registro'))


# Ruta para eliminar un usuario existente
@app.route('/borrar_usuario/<int:user_id>', methods=['POST'])
@login_required
@roles_required('ADMIN')
def borrar_usuario(user_id):
    user = User.query.get_or_404(user_id)
    
    db.session.delete(user)
    mail = Email.query.get(user_id)
    if mail:
        db.session.delete(mail)
    db.session.commit()
    flash('Usuario eliminado exitosamente!', 'success')
    return redirect(url_for('registro'))

########### /////////// #########

############################ ////////////// ###################################################


############################ aplicaiones ###################################################


########### inventario #########
@app.route('/inventario')
def inventario():
    # Consultar categorías y elementos desde la base de datos
    categories = Category.query.all()
    elements = Element.query.all()
    images = os.listdir(app.config['UPLOAD_FOLDER'])

    # Renderizar plantilla y pasar datos
    return render_template('inventario.html', categories=categories, elements=elements,images=images)



@app.route('/crear_categoria', methods=['POST'])
def crear_categoria():
    # Obtener datos enviados por Fetch API (en formato JSON)
    data = request.get_json()
    category_name = data.get('categoryName', None)

    if category_name:
        # Verificar si la categoría ya existe
        existing_category = Category.query.filter_by(name=category_name).first()
        
        if existing_category:
            return jsonify({'message': 'La categoría ya existe.'}), 400  # Error: categoría ya existe

        # Crear nueva categoría
        nueva_categoria = Category(name=category_name)
        db.session.add(nueva_categoria)
        db.session.commit()

        return jsonify({'message': 'Categoría creada exitosamente.'}), 200  # Respuesta de éxito

    return jsonify({'message': 'Debe ingresar un nombre para la categoría.'}), 400  # Error: nombre no válido


@app.route('/borrar_category/<int:IDcategory>', methods=['POST'])
def borrar_category(IDcategory):

    try:
        elm_cat = ElementCategory.query.get(IDcategory)
        db.session.delete(elm_cat)
    except:
        pass

    cat = Category.query.get_or_404(IDcategory)
    db.session.delete(cat)

    db.session.commit()
    flash('Elemento eliminado', 'success')
    return redirect(url_for('inventario'))



@app.route('/subir_elemento', methods=['POST'])
def subir_elemento():
    # Obtener datos del FormData
    name = request.form.get('name')
    quantity = request.form.get('quantity')
    description = request.form.get('description')
    categories = request.form.get('categories')
    image = request.files.get('image')
    choose_image = request.form.get('ChooseElementImage')

    # Verificar si los campos obligatorios están presentes
    if not name or not quantity or not categories or (image and choose_image):
        return jsonify({'message': 'Faltan campos obligatorios.'}), 400


    # Verificar si el archivo es permitido
    if image and not allowed_file(image.filename):
        return jsonify({'message': 'Tipo de archivo no permitido.'}), 400

    # Guardar la imagen de manera segura
    if choose_image:
        filename = choose_image
    else:
        filename = ramdom_string_img(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        image_path='static/uploads/'+filename
    # Crear el nuevo elemento
    nuevo_elemento = Element(name=name,disp=True, cantotal=quantity,candisp=quantity, adds=description, img=filename)

    # Añadir a la base de datos
    db.session.add(nuevo_elemento)
    db.session.commit()

    # Asignar las categorías
    category_ids = json.loads(categories)
    for cat_id in category_ids:
        categoria = Category.query.get(cat_id)
        if categoria:
            elemento_categoria = ElementCategory(IDcategory=categoria.IDcategory, IDelement=nuevo_elemento.IDelement)
            db.session.add(elemento_categoria)

    db.session.commit()

    return jsonify({'message': 'Elemento subido exitosamente.'}), 200


@app.route('/borrar_elemento/<int:IDelement>', methods=['POST'])
def borrar_elemento(IDelement):
 
    element = Element.query.get_or_404(IDelement)

    elm_car = ElementCategory.query.get(IDelement)

    if element.img:
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], element.img))
                    except FileNotFoundError:
                        pass 
    if element:
        db.session.delete(element)
    if elm_car:
        db.session.delete(elm_car)

    db.session.commit()
    flash('Elemento eliminado', 'success')
    return redirect(url_for('inventario'))


@app.route('/filtrar_elementos', methods=['GET'])
def filtrar_elementos():
    # Obtener los filtros de la URL
    name_filter = request.args.get('name', '').strip()
    categories_filter = request.args.get('categories', '')

    # Iniciar una consulta base para los elementos
    query = db.session.query(Element)
    filtro=[0]
    # Aplicar filtro por nombre si está presente
    if name_filter:
        query = query.filter(Element.name.ilike(f"%{name_filter}%"))

    # Aplicar filtro por categorías si hay categorías seleccionadas
    if categories_filter:
        category_ids = [int(c) for c in categories_filter.split(',')]

        filtro = Category.query.filter(Category.IDcategory.in_(category_ids))
        filtro = filtro.all()

        query = query.join(ElementCategory).filter(ElementCategory.IDcategory.in_(category_ids))

    # Ejecutar la consulta y obtener los elementos que coinciden con los filtros
    elementos_filtrados = query.all()
    
    # Obtener todas las categorías para mostrarlas en el filtro
    categorias = Category.query.all()

    # Renderizar la plantilla con los elementos filtrados
    if filtro:
        return render_template('inventario.html', categories=categorias, elements=elementos_filtrados,filtro=filtro)
    
    return render_template('inventario.html', categories=categorias, elements=elementos_filtrados)

########### /////////// #########


########### Localizaciones #########
@app.route('/localizacion')
def localizacion():
    ## Obtener todas las localizaciones cargadas
    locations = Location.query.all()
    
    
    
    return render_template('locations.html', locations=locations)

########### /////////// #########

@app.route('/add_location', methods=['POST'])
def add_location():
    # Obtener datos del FormData
    name = request.form.get('name')
    planta = request.form.get('floor')
    description = request.form.get('description')
    image = request.files.get('image')

    # Verificar si los campos obligatorios están presentes
    if not name:
        return jsonify({'message': 'Faltan campos obligatorios.'}), 400

    # Verificar si el archivo es permitido
    if image:
        if not allowed_file(image.filename):
            return jsonify({'message': 'Tipo de archivo no permitido.'}), 400
        # Guardar la imagen de manera segura
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        image_path='static/uploads/'+filename
    else:
        filename = 'building.png'
    # Crear el nuevo elemento
    nueva_localizacion = Location(name=name, planta=planta, descrip=description, img=filename)

    # Añadir a la base de datos
    db.session.add(nueva_localizacion)
    db.session.commit()


    return jsonify({'message': 'Localizacion cargada.'}), 200

@app.route('/borrar_location/<int:id>', methods=['POST'])
def borrar_location(id):
    location = Location.query.get_or_404(id)

    if location.img:
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], location.img))
                    except FileNotFoundError:
                        pass 
    
    db.session.delete(location)
    db.session.commit()
    flash('Localizacion eliminada', 'success')
    return redirect(url_for('localizacion'))
############################ ////////////// ###################################################



############################ Locura maximaaaa ###################################################

@app.route('/elements', methods=['GET'])
def get_elements():
    categories = request.args.getlist('categories[]')  # Filtros de categorías seleccionados
    query = db.session.query(Element)  # Empezamos la consulta con los elementos
    
    if categories:  # Si hay filtros de categoría seleccionados
        query = query.join(ElementCategory).filter(ElementCategory.IDcategory.in_(categories))

    # Ordenamos por disponibilidad y por ID de elemento
    elements = query.order_by(Element.disp.desc(), Element.IDelement).all()

    # Construimos la lista de elementos con la información que necesitamos
    elements_data = [{'IDelement': e.IDelement, 'name': e.name, 'disp': e.disp, 'candisp': e.candisp, 'img': e.img} for e in elements]
    
    return jsonify(elements_data)

@app.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    categories_data = [{'IDcategory': c.IDcategory, 'name': c.name} for c in categories]
    return jsonify(categories_data)


@app.route('/locations', methods=['GET'])
def get_locations():
    locations = Location.query.all()
    locations_data = [{'id': loc.id, 'name': loc.name} for loc in locations]
    return jsonify(locations_data)

############### carrito ###############
#


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'GET':
        # Renderizar la página de checkout con la lista de elementos seleccionados
        return render_template('PEDIDOS/carrito.html')
    
    if request.method == 'POST':
        data = request.json  # Datos enviados desde el frontend (elementos seleccionados, cantidades, etc.)
        IDuser = current_user.IDuser 

        # Convertir la fecha enviada como string a un objeto datetime.date
        order_date = datetime.strptime(data['date'], '%Y-%m-%d').date()

        # Convertir la hora enviada como string a un objeto datetime.time
        order_time = datetime.strptime(data['time'], '%H:%M').time()  # Asegúrate de que 'time' sea parte de los datos enviados

        # Crear la orden con la localización seleccionada
        new_order = Order(
            IDuser=IDuser,
            date=order_date,  # Pasamos la fecha como un objeto date de Python
            time=order_time,
            location=data['location'],  # Localización seleccionada por el usuario
            state='Pendiente'
        )
        db.session.add(new_order)
        db.session.flush()  # Para obtener el ID de la orden recién creada

        # Insertar los elementos del pedido en la tabla OrderElement
        for item in data['items']:
            order_element = OrderElement(IDorder=new_order.IDorder, IDelement=item['IDelement'], cant=item['quantity'])
            db.session.add(order_element)

        db.session.commit()
        return jsonify({'success': True})

############################ ////////////// ###################################################


############################ orders ###################################################

@app.route('/orders', methods=['GET'])
def show_orders():
    orders = Order.query.join(Location, Location.id == Order.location) \
                        .join(OrderElement, Order.IDorder == OrderElement.IDorder) \
                        .join(Element, Element.IDelement == OrderElement.IDelement) \
                        .join(User, User.IDuser == Order.IDuser) \
                        .order_by(Order.state.desc(), Order.IDorder.desc()) \
                        .all()


    # Se obtienen todas las órdenes junto a sus localizaciones y elementos.
    return render_template('verif_pedidos.html', orders=orders)



@app.route('/update_order', methods=['POST'])
def update_order():
    data = request.form  # Recibir datos del formulario enviado con POST
    
    # Obtener la orden que queremos actualizar
    order = Order.query.filter_by(IDorder=data['IDorder']).first()
    
    if order is None:
        flash('Orden no encontrada', 'error')
        return redirect('/orders')

    new_state = data['state']
    old_state = order.state

    # Actualizar el estado de la orden
    order.state = new_state

    for elm_id, cant in zip(data.getlist('IDelement'), data.getlist('cant')):
        order_element = OrderElement.query.filter_by(IDelement=elm_id, IDorder=order.IDorder).first()
        element = Element.query.filter_by(IDelement=elm_id).first()

        if order_element is None or element is None:
            continue

        new_cant = int(cant)
        old_cant = order_element.cant

        # Actualizar la cantidad en OrderElement
        order_element.cant = new_cant

        # Ajustar la cantidad disponible en Element
        if old_state == 'Entregado' and new_state != 'Entregado':
            # Si el estado anterior era 'Entregado', devolvemos los elementos al inventario
            element.candisp += old_cant
        elif old_state != 'Entregado' and new_state == 'Entregado':
            # Si el nuevo estado es 'Entregado', restamos los elementos del inventario
            element.candisp -= new_cant
        elif new_state == 'Devuelto':
            # Si el nuevo estado es 'Devuelto', sumamos la diferencia al inventario
            element.candisp += (new_cant - old_cant)

    if new_state == 'Cancelada':
        # Si el nuevo estado es 'Cancelada', eliminamos la orden y sus elementos
        OrderElement.query.filter_by(IDorder=order.IDorder).delete()
        db.session.delete(order)
    
    try:
        db.session.commit()
        flash('Orden actualizada con éxito', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar la orden: {str(e)}', 'error')

    return redirect('/orders')

############################ ////////////// ###################################################


from waitress import serve

if __name__ == "__main__":
    # Iniciar el servidor usando Waitress
    serve(app, host='0.0.0.0', port=5010)