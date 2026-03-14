from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from conexion.conexion import conectar
import json
import csv

app = Flask(__name__)

#CONFIGURACIÓN SQLITE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#MODELO PRODUCTO (SQLite)
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    cantidad = db.Column(db.Integer)
    precio = db.Column(db.Float)

with app.app_context():
    db.create_all()

#PAGINA PRINCIPAL
@app.route("/")
def inicio():
    return render_template("index.html")

#PAGINA ACERCA DE
@app.route("/about")
def about():
    return render_template("about.html")

#MOSTRAR PRODUCTOS SQLITE
@app.route("/productos")
def productos():
    productos = Producto.query.all()
    return render_template("productos.html", productos=productos)

#AGREGAR PRODUCTO SQLITE
@app.route("/agregar", methods=["GET","POST"])
def agregar():
    if request.method == "POST":
        id = request.form["id"]
        nombre = request.form["nombre"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]
        producto = Producto(
            id=id,
            nombre=nombre,
            cantidad=cantidad,
            precio=precio
        )
        db.session.add(producto)
        db.session.commit()

        #GUARDAR EN TXT
        with open("inventario/data/datos.txt","a") as archivo:
            archivo.write(f"{id},{nombre},{cantidad},{precio}\n")

        #GUARDAR EN JSON
        datos_json = {
            "id": id,
            "nombre": nombre,
            "cantidad": cantidad,
            "precio": precio
        }
        with open("inventario/data/datos.json","a") as archivo:
            json.dump(datos_json,archivo)
            archivo.write("\n")

        #GUARDAR EN CSV
        with open("inventario/data/datos.csv","a",newline="") as archivo:
            writer = csv.writer(archivo)
            writer.writerow([id,nombre,cantidad,precio])
        return redirect("/productos")
    return render_template("producto_form.html")

#MOSTRAR DATOS ARCHIVOS
@app.route("/datos")
def datos():
    txt = open("inventario/data/datos.txt").read()
    with open("inventario/data/datos.json") as archivo:
        json_data = archivo.readlines()
    with open("inventario/data/datos.csv") as archivo:
        csv_data = archivo.readlines()
    return render_template(
        "datos.html",
        txt=txt,
        json_data=json_data,
        csv_data=csv_data
    )

#MYSQL - MOSTRAR PRODUCTOS

@app.route("/mysql_productos")
def mysql_productos():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    return render_template("mysql_productos.html", productos=productos)

#MYSQL - AGREGAR PRODUCTO
@app.route("/mysql_agregar", methods=["GET","POST"])
def mysql_agregar():
    if request.method == "POST":
        id = request.form["id"]
        nombre = request.form["nombre"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]
        conexion = conectar()
        cursor = conexion.cursor()
        sql = "INSERT INTO productos VALUES(%s,%s,%s,%s)"
        valores = (id,nombre,cantidad,precio)
        cursor.execute(sql,valores)
        conexion.commit()
        return redirect("/mysql_productos")
    return render_template("producto_form.html")

#MYSQL - ELIMINAR PRODUCTO
@app.route("/mysql_eliminar/<id>")
def mysql_eliminar(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE id=%s",(id,))
    conexion.commit()
    return redirect("/mysql_productos")

#EJECUTAR APLICACIÓN
if __name__ == "__main__":
    app.run(debug=True)