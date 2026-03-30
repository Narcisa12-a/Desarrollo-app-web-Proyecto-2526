from conexion.conexion import conectar

def obtener_productos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    datos = cursor.fetchall()
    conn.close()
    return datos

def obtener_producto(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE id_producto=%s", (id,))
    dato = cursor.fetchone()
    conn.close()
    return dato

def insertar_producto(nombre, cantidad, precio, stock):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO productos (nombre, cantidad, precio, stock) VALUES (%s, %s, %s, %s)",
        (nombre, cantidad, precio, stock)
    )
    conn.commit()
    conn.close()

def actualizar_producto(id, nombre, cantidad, precio, stock):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE productos SET nombre=%s, cantidad=%s, precio=%s, stock=%s WHERE id_producto=%s",
        (nombre, cantidad, precio, stock, id)
    )
    conn.commit()
    conn.close()

def eliminar_producto_db(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id_producto=%s", (id,))
    conn.commit()
    conn.close()