"""Demostración del reto obligatorio: error controlado + rollback()."""
import db


def estado(conn, etiqueta, pid):
    p = db.obtener_producto(conn, pid)
    print(f"[{etiqueta}] stock de '{p['nombre']}': {p['cantidad']} | "
          f"ventas registradas: {db.contar_ventas(conn)}")


def main():
    conn = db.conectar(":memory:")
    db.crear_tablas(conn)
    pid = db.registrar_producto(conn, "Arduino Uno R3", 85000, 10)

    print("=== DEMO ROLLBACK ===")
    estado(conn, "ANTES  ", pid)

    print("\n-> Venta normal de 2 unidades (debe confirmarse)")
    db.registrar_venta(conn, pid, 2)
    estado(conn, "TRAS OK", pid)

    print("\n-> Venta de 3 unidades con ERROR SIMULADO tras el INSERT")
    try:
        db.registrar_venta(conn, pid, 3, simular_error=True)
    except db.ErrorSimulado as e:
        print(f"   Error capturado: {e}")
        print("   rollback() ejecutado: la venta insertada se canceló.")
    estado(conn, "TRAS ERR", pid)

    p = db.obtener_producto(conn, pid)
    assert p["cantidad"] == 8 and db.contar_ventas(conn) == 1
    print("\nVERIFICACION: stock=8 y 1 venta -> datos INTACTOS tras el error. OK")


if __name__ == "__main__":
    main()
