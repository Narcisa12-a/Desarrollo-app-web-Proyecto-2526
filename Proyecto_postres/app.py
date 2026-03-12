from flask import Flask, render_template

app = Flask(__name__)

# Página principal
@app.route("/")
def inicio():
    return render_template("index.html")

# Página acerca de
@app.route("/about")
def about():
    return render_template("about.html")

# Página de productos
@app.route("/productos")
def productos():
    return render_template("productos.html")

# Ruta dinámica para pedidos
@app.route("/pedido/<cliente>")
def pedido(cliente):
    return f"Hola {cliente}, tu pedido de postres está en preparación."

if __name__ == "__main__":
    app.run(debug=True)