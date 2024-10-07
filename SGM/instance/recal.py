from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, Text, Time, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker,declarative_base

# Crear una instancia base para las clases de las tablas
Base = declarative_base()

# Definir las clases que representan las tablas
class Category(Base):
    __tablename__ = 'category'
   
    IDcategory = Column(Integer, primary_key=True, autoincrement=True)
    cat_name = Column(String(255), nullable=False)

class Element(Base):
    __tablename__ = 'elements'
   
    IDelement = Column(Integer, primary_key=True, autoincrement=True)
    el_name = Column(String(255), nullable=False)
    el_disp = Column(Integer, nullable=False)
    el_cant = Column(Integer, nullable=False)
    el_adds = Column(String(255), nullable=True)
    el_img = Column(String(255), nullable=True)

class ElementCategory(Base):
    __tablename__ = 'elm_category'
   
    IDcategory = Column(Integer, ForeignKey('category.IDcategory'), primary_key=True)
    IDelement = Column(Integer, ForeignKey('elements.IDelement'), primary_key=True)

class Email(Base):
    __tablename__ = 'email'
   
    IDemail = Column(Integer, primary_key=True, autoincrement=True)
    IDuser = Column(Integer, nullable=False)
    address = Column(String(45), nullable=False)

class Maintenance(Base):
    __tablename__ = 'maintenance'
   
    IDmaintenance = Column(Integer, primary_key=True, autoincrement=True)
    ma_date = Column(Date, nullable=False)
    ma_details = Column(String(255), nullable=True)
    ma_repeat = Column(Integer, nullable=False)
    ma_state = Column(String(255), nullable=False)

class MaintenanceElement(Base):
    __tablename__ = 'maintenance_elm'
   
    IDmantenance = Column(Integer, ForeignKey('maintenance.IDmaintenance'), primary_key=True)
    IDelement = Column(Integer, ForeignKey('elements.IDelement'))
    revised = Column(Integer, nullable=True)
    details = Column(String(255), nullable=True)

class Order(Base):
    __tablename__ = 'orders'
   
    IDorder = Column(Integer, primary_key=True, autoincrement=True)
    order_time = Column(Time, nullable=False)
    order_date = Column(Date, nullable=False)
    order_location = Column(String(255), nullable=False)
    order_repeat = Column(Integer, nullable=False)
    order_finish = Column(Date, nullable=True)
    order_state = Column(String(255), nullable=False)

class OrderElement(Base):
    __tablename__ = 'orders_elm'
   
    IDorder = Column(Integer, ForeignKey('orders.IDorder'), primary_key=True)
    IDelement = Column(Integer, ForeignKey('elements.IDelement'), primary_key=True)

class OrderRep(Base):
    __tablename__ = 'orders_rep'
   
    IDorder = Column(Integer, ForeignKey('orders.IDorder'), primary_key=True)
    repeat_day = Column(String(255), primary_key=True)

class Task(Base):
    __tablename__ = 'tareas'
   
    IDtarea = Column(Integer, primary_key=True, autoincrement=True)
    IDorder = Column(Integer, ForeignKey('orders.IDorder'), nullable=True)
    titulo = Column(String(255), nullable=False)
    cuerpo = Column(String(255), nullable=True)
    fecha_in = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=False)
    prioridad = Column(String(255), nullable=True)
    estado = Column(String(255), nullable=True)

class User(Base):
    __tablename__ = 'user'
   
    IDuser = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False, unique=True)
    userpass = Column(String(255), nullable=False)
    userclass = Column(String(255), nullable=False)
   
    __table_args__ = (
        CheckConstraint('length(userpass) >= 8', name='userpass_check'),
    )

# Crear una base de datos SQLite
engine = create_engine('sqlite:///database.db')

# Crear las tablas en la base de datos
Base.metadata.create_all(engine)

# Crear una sesión
Session = sessionmaker(bind=engine)
session = Session()