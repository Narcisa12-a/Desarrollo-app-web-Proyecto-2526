from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import io

# SERVICIOS
from services.producto_service import *

# CONEXIÓN Y MODELOS
from conexion.conexion import conectar
from models.usuario import Usuario

# PDF
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

app = Flask(__name__)
app.secret_key = "clave_secreta"

# =========================
# 🔐 LOGIN
# =========================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
    user = cursor.fetchone()
    conexion.close()

    if user:
        return Usuario(user[0], user[1], user[2], user[3])  # 👈 4 campos
    return None


# =========================
# 🏠 INICIO / ACERCA
# =========================
@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/acerca")
def acerca():
    return render_template("about.html")


# =========================
# 🔐 LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT * FROM usuarios WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()
        conexion.close()

        if user:
            usuario = Usuario(user[0], user[1], user[2], user[3])
            login_user(usuario)
            return redirect(url_for("inicio"))

    return render_template("login.html")


# =========================
# 📝 REGISTRO
# =========================
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
            (nombre, email, password)
        )

        conexion.commit()
        conexion.close()

        return redirect(url_for("login"))

    return render_template("registro.html")


# =========================
# 🚪 LOGOUT
# =========================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# =========================
# 🧁 PRODUCTOS (CRUD)
# =========================
@app.route("/productos")
@login_required
def listar_productos():
    productos = obtener_productos()
    return render_template("productos/lista.html", productos=productos)


@app.route("/productos/crear", methods=["GET", "POST"])
@login_required
def crear_producto():
    if request.method == "POST":
        nombre = request.form["nombre"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]
        stock = request.form["stock"]

        insertar_producto(nombre, cantidad, precio, stock)

        return redirect(url_for("listar_productos"))

    return render_template("productos/crear.html")


@app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_producto(id):
    if request.method == "POST":
        nombre = request.form["nombre"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]
        stock = request.form["stock"]

        actualizar_producto(id, nombre, cantidad, precio, stock)

        return redirect(url_for("listar_productos"))

    producto = obtener_producto_por_id(id)
    return render_template("productos/editar.html", producto=producto)


@app.route("/productos/eliminar/<int:id>")
@login_required
def eliminar_producto(id):
    eliminar_producto_db(id)
    return redirect(url_for("listar_productos"))


# =========================
# 👤 CLIENTES
# =========================
@app.route("/clientes")
@login_required
def listar_clientes():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()

    conexion.close()
    return render_template("clientes/lista.html", clientes=clientes)


# =========================
# 🧾 VENTAS (JOIN)
# =========================
@app.route("/ventas")
@login_required
def listar_ventas():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT v.id_venta, c.nombre, p.nombre, v.cantidad
        FROM ventas v
        JOIN clientes c ON v.id_cliente = c.id_cliente
        JOIN productos p ON v.id_producto = p.id_producto
    """)

    ventas = cursor.fetchall()
    conexion.close()

    return render_template("ventas/lista.html", ventas=ventas)


# =========================
# 📄 PDF
# =========================
@app.route("/reporte_pdf")
@login_required
def reporte_pdf():
    buffer = io.BytesIO()

    # Crear documento
    doc = SimpleDocTemplate(buffer)

    elementos = []

    # Estilos
    estilos = getSampleStyleSheet()

    # TÍTULO
    titulo = Paragraph("🍰 Cat Cake - Reporte de Productos", estilos['Title'])
    elementos.append(titulo)

    # FECHA
    fecha = Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", estilos['Normal'])
    elementos.append(fecha)

    # Espacio
    elementos.append(Paragraph("<br/><br/>", estilos['Normal']))

    # DATOS
    productos = obtener_productos()

    # Encabezados
    data = [["ID", "Nombre", "Cantidad", "Precio", "Stock"]]

    # Filas
    for p in productos:
        data.append([p[0], p[1], p[2], f"${p[3]}", p[4]])

    # Crear tabla
    tabla = Table(data)

    # Estilo de tabla
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.pink),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

        ('GRID', (0, 0), (-1, -1), 1, colors.black),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elementos.append(tabla)

    # Construir PDF
    doc.build(elementos)

    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="reporte_productos.pdf")

# =========================
# ▶️ EJECUTAR
# =========================
if __name__ == "__main__":
    app.run(debug=True)