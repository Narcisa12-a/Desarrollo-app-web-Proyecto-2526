from flask import Flask
#Crear la aplicacion Flask
app = Flask (__name__)
#Ruta principal 
@app.route("/")
def inicio():
    return "Bienvenido a Cat Cake- Tienda de Postres Online"

#Ruta dinamica para productos
@app.route("/postre/<nombre>")
def postre(nombre):
    return f"Postre: {nombre} - Disponible en nuestra tienda."

#Ruta dinamica para pedidos
@app.route("/pedido/<cliente>")
def pedido(cliente):
    return f"Hola: {cliente},tu pedido de postres esta en preparación"

#Ejecutar la aplicacion
if __name__ == "__main__":
    app.run(debug=True)