class Inventario:

    def __init__(self):
        self.productos = {}

    def agregar_producto(self, producto):
        self.productos[producto.id] = producto

    def eliminar_producto(self, id):
        if id in self.productos:
            del self.productos[id]

    def mostrar_productos(self):
        return list(self.productos.values())