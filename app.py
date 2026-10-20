
"""Aplicación de consola: inventario y ventas con SQLite."""
import db


def pedir_int(msg):
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("  Ingresa un número entero válido.")


def pedir_float(msg):
    while True:
        try:
            return float(input(msg))
        except ValueError:
            print("  Ingresa un número válido.")


def mostrar_productos(conn):
    filas = db.listar_productos(conn)
    if not filas:
        print("  (No hay productos registrados)")
        return
    print(f"  {'ID':<4}{'Nombre':<28}{'Precio':>12}{'Cantidad':>10}")
    for f in filas:
        print(f"  {f['id']:<4}{f['nombre']:<28}{f['precio']:>12,.0f}{f['cantidad']:>10}")


def menu_registrar(conn):
    nombre = input("Nombre: ").strip()
    if not nombre:
        print("  El nombre no puede estar vacío.")
        return
    precio = pedir_float("Precio: ")
    cantidad = pedir_int("Cantidad disponible: ")
    pid = db.registrar_producto(conn, nombre, precio, cantidad)
    print(f"  Producto registrado con ID {pid}.")


def menu_actualizar(conn):
    pid = pedir_int("ID del producto: ")
    print("  1) Precio   2) Cantidad")
    op = input("  Qué actualizar: ").strip()
    if op == "1":
        db.actualizar_producto(conn, pid, precio=pedir_float("Nuevo precio: "))
    elif op == "2":
        db.actualizar_producto(conn, pid, cantidad=pedir_int("Nueva cantidad: "))
    else:
        print("  Opción no válida.")
        return
    print("  Producto actualizado.")


def menu_eliminar(conn):
    db.eliminar_producto(conn, pedir_int("ID del producto a eliminar: "))
    print("  Producto eliminado.")


def menu_venta(conn, simular=False):
    pid = pedir_int("ID del producto: ")
    cant = pedir_int("Cantidad a vender: ")
    vid, total = db.registrar_venta(conn, pid, cant, simular_error=simular)
    print(f"  Venta #{vid} registrada. Total: {total:,.0f}")


def menu_historial(conn):
    filas = db.historial_ventas(conn)
    if not filas:
        print("  (No hay ventas registradas)")
        return
    print(f"  {'ID':<4}{'Producto':<24}{'Cant':>5}{'Total':>12}  Fecha")
    for f in filas:
        print(f"  {f['id']:<4}{f['nombre']:<24}{f['cantidad']:>5}{f['total']:>12,.0f}  {f['fecha']}")


def menu_demo_rollback(conn):
    print("  Se intentará una venta con un error simulado tras insertarla.")
    pid = pedir_int("ID del producto: ")
    cant = pedir_int("Cantidad: ")
    antes = db.obtener_producto(conn, pid)
    ventas_antes = db.contar_ventas(conn)
    try:
        db.registrar_venta(conn, pid, cant, simular_error=True)
    except db.ErrorSimulado as e:
        print(f"  Error controlado: {e}\n  -> rollback() ejecutado.")
    except db.ErrorNegocio as e:
        print(f"  {e}")
        return
    despues = db.obtener_producto(conn, pid)
    print(f"  Stock antes: {antes['cantidad']} | después: {despues['cantidad']}")
    print(f"  Ventas antes: {ventas_antes} | después: {db.contar_ventas(conn)}")
    ok = antes["cantidad"] == despues["cantidad"] and ventas_antes == db.contar_ventas(conn)
    print("  Verificación:", "DATOS INTACTOS" if ok else "¡INCONSISTENCIA!")


MENU = """
===== TIENDA DE COMPONENTES ELECTRÓNICOS =====
 1. Registrar producto
 2. Consultar productos
 3. Actualizar precio o cantidad
 4. Eliminar producto
 5. Registrar venta
 6. Historial de ventas
 7. Demostrar rollback (error controlado)
 0. Salir
"""


def main():
    conn = db.conectar()
    db.crear_tablas(conn)
    acciones = {
        "1": menu_registrar,
        "2": mostrar_productos,
        "3": menu_actualizar,
        "4": menu_eliminar,
        "5": menu_venta,
        "6": menu_historial,
        "7": menu_demo_rollback,
    }
    while True:
        print(MENU)
        op = input("Elige una opción: ").strip()
        if op == "0":
            print("Hasta luego.")
            break
        accion = acciones.get(op)
        if accion is None:
            print("  Opción no válida.")
            continue
        try:
            accion(conn)
        except db.ErrorNegocio as e:
            print(f"  ERROR: {e}")
        except EOFError:
            break
    conn.close()


if __name__ == "__main__":
    main()
