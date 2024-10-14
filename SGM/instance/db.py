import sqlite3

# Conectar a la base de datos SQLite (se crea si no existe)
conn = sqlite3.connect('SGM/instance/database.db')
cursor = conn.cursor()

# Crear las tablas
cursor.executescript('''
CREATE TABLE category (
  IDcategory INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  cat_name TEXT NOT NULL
);

CREATE TABLE elements (
  IDelement INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  el_name TEXT NOT NULL,
  el_disp INTEGER NOT NULL,
  el_cant INTEGER NOT NULL,
  el_adds TEXT DEFAULT NULL,
  el_img TEXT DEFAULT NULL
);

CREATE TABLE elm_category (
  IDcategory INTEGER NOT NULL,
  IDelement INTEGER NOT NULL,
  PRIMARY KEY (IDcategory, IDelement),
  FOREIGN KEY (IDcategory) REFERENCES category(IDcategory),
  FOREIGN KEY (IDelement) REFERENCES elements(IDelement)
);

CREATE TABLE email (
  IDemail INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  IDuser INTEGER NOT NULL,
  address TEXT NOT NULL
);

CREATE TABLE maintenance (
  IDmaintenance INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  ma_date DATE NOT NULL,
  ma_details TEXT DEFAULT NULL,
  ma_repeat INTEGER NOT NULL,
  ma_state TEXT NOT NULL
);

CREATE TABLE maintenance_elm (
  IDmaintenance INTEGER NOT NULL,
  IDelement INTEGER NOT NULL,
  revised INTEGER DEFAULT NULL,
  details TEXT DEFAULT NULL,
  PRIMARY KEY (IDmaintenance),
  FOREIGN KEY (IDelement) REFERENCES elements(IDelement)
);

CREATE TABLE orders (
  IDorder INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  order_time TEXT NOT NULL,
  order_date DATE NOT NULL,
  order_location TEXT NOT NULL,
  order_repeat INTEGER NOT NULL,
  order_finish DATE DEFAULT NULL,
  order_state TEXT NOT NULL
);

CREATE TABLE orders_elm (
  IDorder INTEGER NOT NULL,
  IDelement INTEGER NOT NULL,
  PRIMARY KEY (IDorder, IDelement),
  FOREIGN KEY (IDorder) REFERENCES orders(IDorder),
  FOREIGN KEY (IDelement) REFERENCES elements(IDelement)
);

CREATE TABLE orders_rep (
  IDorder INTEGER NOT NULL,
  repeat_day TEXT NOT NULL,
  PRIMARY KEY (IDorder, repeat_day),
  FOREIGN KEY (IDorder) REFERENCES orders(IDorder)
);

CREATE TABLE tareas (
  IDtarea INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  IDorder INTEGER DEFAULT NULL,
  titulo TEXT NOT NULL,
  cuerpo TEXT DEFAULT NULL,
  fecha_in DATE DEFAULT NULL,
  fecha_fin DATE NOT NULL,
  prioridad TEXT DEFAULT NULL,
  estado TEXT DEFAULT NULL,
  FOREIGN KEY (IDorder) REFERENCES orders(IDorder)
);

CREATE TABLE user (
  IDuser INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  userpass TEXT NOT NULL,
  userclass TEXT NOT NULL,
  CHECK (length(userpass) >= 8)
);
''')

# Confirmar cambios y cerrar la conexión
conn.commit()
conn.close()
