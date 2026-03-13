from flask import Flask, render_template, request, redirect
import sqlite3
from inventario.bd import crear_tabla

app = Flask(__name__)

# Crear la base de datos si no existe
crear_tabla()

# PAGINA PRINCIPAL
@app.route("/")
def inicio():
    return render_template("index.html")

# PAGINA ACERCA DE
@app.route("/about")
def about():
    return render_template("about.html")

# MOSTRAR PRODUCTOS
@app.route("/productos")
def productos():
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos")
    lista_productos = cursor.fetchall()
    conexion.close()
    return render_template("productos.html", productos=lista_productos)

# AGREGAR PRODUCTO
@app.route("/agregar", methods=["GET","POST"])
def agregar():
    if request.method == "POST":
        id = request.form["id"]
        nombre = request.form["nombre"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]
        conexion = sqlite3.connect("inventario.db")
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO productos VALUES(?,?,?,?)",
            (id, nombre, cantidad, precio)
        )
        conexion.commit()
        conexion.close()
        return redirect("/productos")
    return render_template("producto_form.html")

# RUTA DINAMICA PEDIDOS
@app.route("/pedido/<cliente>")
def pedido(cliente):
    return f"Hola {cliente}, tu pedido de postres está en preparación."

# EJECUTAR APP
if __name__ == "__main__":
    app.run(debug=True)