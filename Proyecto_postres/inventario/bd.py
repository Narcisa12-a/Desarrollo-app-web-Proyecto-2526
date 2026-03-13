import sqlite3

def conectar():
    return sqlite3.connect("inventario.db")

def crear_tabla():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos(
        id INTEGER PRIMARY KEY,
        nombre TEXT,
        cantidad INTEGER,
        precio REAL
    )
    """)

    conexion.commit()
    conexion.close()