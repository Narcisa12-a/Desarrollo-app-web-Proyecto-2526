from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from conexion.conexion import conectar
from models import Usuario
import json
import csv

app = Flask(__name__)
app.secret_key = "secreto123"

#CONFIGURACIÓN SQLITE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#FLASK LOGIN
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#MODELO SQLITE
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    cantidad = db.Column(db.Integer)
    precio = db.Column(db.Float)
with app.app_context():
    db.create_all()

#CARGAR USUARIO DESDE MYSQL
@login_manager.user_loader
def load_user(user_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario=%s", (user_id,))
    user = cursor.fetchone()
    if user:
        return Usuario(user[0], user[1], user[2], user[3])
    return None

#PAGINAS PRINCIPALES
@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

#REGISTRO
@app.route("/registro", methods=["GET","POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        mail = request.form["mail"]
        password = request.form["password"]
        conexion = conectar()
        cursor = conexion.cursor()
        sql = "INSERT INTO usuarios(nombre,mail,password) VALUES(%s,%s,%s)"
        cursor.execute(sql,(nombre,mail,password))
        conexion.commit()
        return redirect("/login")
    return render_template("registro.html")

#LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        mail = request.form["mail"]
        password = request.form["password"]
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE mail=%s AND password=%s",(mail,password))
        user = cursor.fetchone()
        if user:
            usuario = Usuario(user[0], user[1], user[2], user[3])
            login_user(usuario)
            return redirect("/dashboard")
    return render_template("login.html")

#DASHBOARD PROTEGIDO
@app.route("/dashboard")
@login_required
def dashboard():
    return f"Bienvenido {current_user.nombre}, estás logueado"

#LOGOUT
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

#SQLITE - PRODUCTOS
@app.route("/productos")
@login_required
def productos():
    productos = Producto.query.all()
    return render_template("productos.html", productos=productos)

#AGREGAR SQLITE + ARCHIVOS
@app.route("/agregar", methods=["GET","POST"])
@login_required
def agregar():
    if request.method == "POST":
        id = request.form["id"]
        nombre = request.form["nombre"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]
        producto = Producto(id=id, nombre=nombre, cantidad=cantidad, precio=precio)
        db.session.add(producto)
        db.session.commit()
        #TXT
        with open("inventario/data/datos.txt","a") as f:
            f.write(f"{id},{nombre},{cantidad},{precio}\n")
        #JSON
        data = {"id":id,"nombre":nombre,"cantidad":cantidad,"precio":precio}
        with open("inventario/data/datos.json","a") as f:
            json.dump(data,f)
            f.write("\n")
        #CSV
        with open("inventario/data/datos.csv","a",newline="") as f:
            writer = csv.writer(f)
            writer.writerow([id,nombre,cantidad,precio])
        return redirect("/productos")
    return render_template("producto_form.html")

#VER ARCHIVOS
@app.route("/datos")
@login_required
def datos():
    txt = open("inventario/data/datos.txt").read()
    with open("inventario/data/datos.json") as f:
        json_data = f.readlines()
    with open("inventario/data/datos.csv") as f:
        csv_data = f.readlines()
    return render_template("datos.html", txt=txt, json_data=json_data, csv_data=csv_data)

#MYSQL - PRODUCTOS
@app.route("/mysql_productos")
@login_required
def mysql_productos():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    return render_template("mysql_productos.html", productos=productos)

#MYSQL - AGREGAR
@app.route("/mysql_agregar", methods=["GET","POST"])
@login_required
def mysql_agregar():
    if request.method == "POST":
        id = request.form["id"]
        nombre = request.form["nombre"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO productos VALUES(%s,%s,%s,%s)",
                       (id,nombre,cantidad,precio))
        conexion.commit()
        return redirect("/mysql_productos")
    return render_template("producto_form.html")

#MYSQL - ELIMINAR
@app.route("/mysql_eliminar/<id>")
@login_required
def mysql_eliminar(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE id=%s",(id,))
    conexion.commit()
    return redirect("/mysql_productos")

#EJECUTAR
if __name__ == "__main__":
    app.run(debug=True)