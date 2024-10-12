from flask import Flask, render_template, url_for, redirect, request, flash, session,send_from_directory, jsonify
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
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

app = Flask(__name__)


UPLOAD_FOLDER = 'SGM/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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


@login_manager.user_loader
def load_user(IDuser):
    return User.query.get(int(IDuser))

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
            return (self.IDuser)
    
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
    cant = Column(Integer, nullable=False)
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
    IDuser = Column(Integer, nullable=False) 
    address = Column(String(45), nullable=False)

class Maintenance(db.Model):
    __tablename__ = 'maintenance'
   
    IDmaintenance = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    details = Column(String(255), nullable=True)
    repeat = Column(Integer, nullable=False)
    state = Column(String(255), nullable=False)

class MaintenanceElement(db.Model):
    __tablename__ = 'maintenance_elm'
   
    IDmantenance = Column(Integer, ForeignKey('maintenance.IDmaintenance'), primary_key=True)
    IDelement = Column(Integer, ForeignKey('elements.IDelement'))
    revised = Column(Integer, nullable=True)
    details = Column(String(255), nullable=True)

class Order(db.Model):
    __tablename__ = 'orders'
   
    IDorder = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Time, nullable=False)
    date = Column(Date, nullable=False)
    location = Column(String(255), nullable=False)
    repeat = Column(Integer, nullable=False)
    finish = Column(Date, nullable=True)
    state = Column(String(255), nullable=False)

class OrderElement(db.Model):
    __tablename__ = 'orders_elm'
   
    IDorder = Column(Integer, ForeignKey('orders.IDorder'), primary_key=True)
    IDelement = Column(Integer, ForeignKey('elements.IDelement'), primary_key=True)

class OrderRep(db.Model):
    __tablename__ = 'orders_rep'
   
    IDorder = Column(Integer, ForeignKey('orders.IDorder'), primary_key=True)
    repeat_day = Column(String(255), primary_key=True)

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
                            InputRequired(), Length(min=4, max=45)], render_kw={"placeholder": "Email"})

    password = PasswordField(validators=[
                            InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Contraseña"})
    
    
    rol = SelectField('Roles', choices=[('ADMIN'), ('LV1'), ('LV2'), ('LVL3')])

    submit = SubmitField('Registrar')

###
######## formulario de inicio de sesion ##########

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Usuario"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Contraseña"})

    submit = SubmitField('iniciar sesión')

###


def validate_username(username):
    existing_user_username = User.query.filter_by(
        username=username.data).first()
    if existing_user_username:
        return True



############################ Login ###################################################
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route("/inicio", methods=['GET', 'POST'])
@login_required
def inicio():
    return render_template('inicio.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.userpass, form.password.data):
                login_user(user)
                return redirect(url_for('inicio'))
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
@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    users = User.query.all()
    if form.validate_on_submit():
        if validate_username(form.username):
            flash('El usuario ya existe.', 'warning')
            return redirect(url_for('register'))  
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, userpass=hashed_password,userclass=form.rol.data)
        db.session.add(new_user)

        userid = User.query.filter(
            User.username == form.username.data
        ).first()

        new_mail= Email(IDuser= userid.IDuser,address=form.email.data)
        db.session.add(new_mail)
        db.session.commit()
        flash('Usuario creado.', 'success')
        return redirect(url_for('register'))
    return render_template('REGISTRO/index.html', users=users,form=form)


# Ruta para eliminar un usuario existente
@app.route('/borrar_usuario/<int:user_id>', methods=['POST'])
def borrar_usuario(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Usuario eliminado exitosamente!', 'success')
    return redirect(url_for('register'))

########### /////////// #########

############################ ////////////// ###################################################


############################ aplicaiones ###################################################


########### inventario #########
@app.route('/inventario')
def inventario():
    # Consultar categorías y elementos desde la base de datos
    categories = Category.query.all()
    elements = Element.query.all()
    
    # Renderizar plantilla y pasar datos
    return render_template('inventario.html', categories=categories, elements=elements)



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
        elm_cat = ElementCategory.query.get_or_404(IDcategory)
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

    # Verificar si los campos obligatorios están presentes
    if not name or not quantity or not categories or not image:
        return jsonify({'message': 'Faltan campos obligatorios.'}), 400

    # Verificar si el archivo es permitido
    if not allowed_file(image.filename):
        return jsonify({'message': 'Tipo de archivo no permitido.'}), 400

    # Guardar la imagen de manera segura
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)
    image_path='static/uploads/'+filename
    # Crear el nuevo elemento
    nuevo_elemento = Element(name=name,disp=True, cant=quantity, adds=description, img=filename)

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
    elm_car = ElementCategory.query.get_or_404(IDelement)
    if element.img:
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], element.img))
                    except FileNotFoundError:
                        pass 
    
    db.session.delete(element)
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

    # Aplicar filtro por nombre si está presente
    if name_filter:
        query = query.filter(Element.name.ilike(f"%{name_filter}%"))

    # Aplicar filtro por categorías si hay categorías seleccionadas
    if categories_filter:
        category_ids = [int(c) for c in categories_filter.split(',')]
        query = query.join(ElementCategory).filter(ElementCategory.IDcategory.in_(category_ids))

    # Ejecutar la consulta y obtener los elementos que coinciden con los filtros
    elementos_filtrados = query.all()

    # Obtener todas las categorías para mostrarlas en el filtro
    categorias = Category.query.all()

    # Renderizar la plantilla con los elementos filtrados

    return render_template('inventario/index.html', categories=categorias, elements=elementos_filtrados)

########### /////////// #########


########### Localizaciones #########
@app.route('/localizacion')
def localizacion():
    ## Obtener todas las localizaciones cargadas
    locations = Location.query.all()
    
    
    
    return render_template('locations.html', locations=locations)

########### /////////// #########




############################ ////////////// ###################################################


if __name__ == '__main__':
    app.run()