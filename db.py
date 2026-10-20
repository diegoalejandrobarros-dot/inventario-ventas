"""Capa de acceso a datos del sistema de inventario y ventas (SQLite)."""
import sqlite3
from datetime import datetime

DB_PATH = "tienda.db"


class ErrorSimulado(Exception):
    """Error controlado, usado para demostrar el rollback."""


class ErrorNegocio(Exception):
    """Violación de una regla de negocio (producto inexistente, sin stock...)."""


def conectar(ruta=None):
    conn = sqlite3.connect(ruta or DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite no valida FK por defecto
    return conn


def crear_tablas(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS productos (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre   TEXT    NOT NULL UNIQUE,
            precio   REAL    NOT NULL CHECK (precio >= 0),
            cantidad INTEGER NOT NULL CHECK (cantidad >= 0)
        );
        CREATE TABLE IF NOT EXISTS ventas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            cantidad    INTEGER NOT NULL CHECK (cantidad > 0),
            total       REAL    NOT NULL,
            fecha       TEXT    NOT NULL,
            FOREIGN KEY (producto_id) REFERENCES productos(id)
                ON DELETE RESTRICT
        );
    """)
    conn.commit()


# ---------------------------------------------------------------- CRUD
def registrar_producto(conn, nombre, precio, cantidad):
    try:
        cur = conn.execute(
            "INSERT INTO productos (nombre, precio, cantidad) VALUES (?, ?, ?)",
            (nombre, precio, cantidad),
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ErrorNegocio(f"No se pudo registrar el producto: {e}")


def listar_productos(conn):
    return conn.execute(
        "SELECT id, nombre, precio, cantidad FROM productos ORDER BY id"
    ).fetchall()


def obtener_producto(conn, producto_id):
    return conn.execute(
        "SELECT id, nombre, precio, cantidad FROM productos WHERE id = ?",
        (producto_id,),
    ).fetchone()


def actualizar_producto(conn, producto_id, precio=None, cantidad=None):
    if obtener_producto(conn, producto_id) is None:
        raise ErrorNegocio("El producto no existe.")
    try:
        if precio is not None:
            conn.execute("UPDATE productos SET precio = ? WHERE id = ?",
                         (precio, producto_id))
        if cantidad is not None:
            conn.execute("UPDATE productos SET cantidad = ? WHERE id = ?",
                         (cantidad, producto_id))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ErrorNegocio(f"Valor no válido: {e}")


def eliminar_producto(conn, producto_id):
    """Elimina un producto solo si no tiene ventas asociadas (integridad referencial)."""
    if obtener_producto(conn, producto_id) is None:
        raise ErrorNegocio("El producto no existe.")
    try:
        conn.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        raise ErrorNegocio(
            "No se puede eliminar: el producto tiene ventas registradas en el historial."
        )


# -------------------------------------------------------------- VENTAS
def registrar_venta(conn, producto_id, cantidad, simular_error=False):
    """Registra una venta de forma atómica.

    Pasos: validar -> INSERT venta -> (error opcional) -> UPDATE inventario -> commit.
    Cualquier fallo después del INSERT dispara rollback() y no queda nada guardado.
    """
    if cantidad <= 0:
        raise ErrorNegocio("La cantidad debe ser mayor que cero.")

    producto = obtener_producto(conn, producto_id)           # 1. ¿existe?
    if producto is None:
        raise ErrorNegocio("El producto no existe.")
    if producto["cantidad"] < cantidad:                      # 2. ¿hay stock?
        raise ErrorNegocio(
            f"Stock insuficiente: hay {producto['cantidad']} y se piden {cantidad}."
        )

    total = producto["precio"] * cantidad
    try:
        cur = conn.execute(                                  # 3. registrar venta
            "INSERT INTO ventas (producto_id, cantidad, total, fecha) VALUES (?, ?, ?, ?)",
            (producto_id, cantidad, total, datetime.now().isoformat(timespec="seconds")),
        )
        if simular_error:                                    # error controlado (reto)
            raise ErrorSimulado("Fallo simulado tras insertar la venta.")
        conn.execute(                                        # 4. descontar inventario
            "UPDATE productos SET cantidad = cantidad - ? WHERE id = ?",
            (cantidad, producto_id),
        )
        conn.commit()                                        # 5. confirmar ambas
        return cur.lastrowid, total
    except Exception:
        conn.rollback()                                      # cancelar TODO
        raise


def historial_ventas(conn):
    return conn.execute("""
        SELECT v.id, p.nombre, v.cantidad, v.total, v.fecha
        FROM ventas v
        JOIN productos p ON p.id = v.producto_id
        ORDER BY v.id
    """).fetchall()


def contar_ventas(conn):
    return conn.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
