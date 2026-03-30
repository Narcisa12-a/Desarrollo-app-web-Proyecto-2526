#archivo para formularios 
class ProductoForm:
    def __init__(self):
        self.nombre = type('', (), {})()
        self.precio = type('', (), {})()
        self.stock = type('', (), {})()

        self.nombre.data = ""
        self.precio.data = ""
        self.stock.data = ""