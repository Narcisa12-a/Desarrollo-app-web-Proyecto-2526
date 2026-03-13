from .productos import Producto

class Inventario:

    def __init__(self):
        # Diccionario para almacenar productos
        self.productos = {}

    def agregar_producto(self, producto):
        self.productos[producto.id] = producto

    def eliminar_producto(self, id):
        if id in self.productos:
            del self.productos[id]

    def actualizar_producto(self, id, cantidad=None, precio=None):
        if id in self.productos:
            if cantidad:
                self.productos[id].actualizar_cantidad(cantidad)
            if precio:
                self.productos[id].actualizar_precio(precio)

    def buscar_producto(self, nombre):
        return [p for p in self.productos.values() if p.nombre == nombre]

    def mostrar_productos(self):
        return list(self.productos.values())