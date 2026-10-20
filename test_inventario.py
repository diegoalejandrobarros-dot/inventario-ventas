import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db


class TestInventario(unittest.TestCase):
    def setUp(self):
        self.conn = db.conectar(":memory:")
        db.crear_tablas(self.conn)
        self.pid = db.registrar_producto(self.conn, "Resistencia 1k", 100, 10)

    def test_venta_ok(self):
        db.registrar_venta(self.conn, self.pid, 4)
        self.assertEqual(db.obtener_producto(self.conn, self.pid)["cantidad"], 6)
        self.assertEqual(db.contar_ventas(self.conn), 1)

    def test_producto_inexistente(self):
        with self.assertRaises(db.ErrorNegocio):
            db.registrar_venta(self.conn, 999, 1)

    def test_stock_insuficiente(self):
        with self.assertRaises(db.ErrorNegocio):
            db.registrar_venta(self.conn, self.pid, 11)
        self.assertEqual(db.contar_ventas(self.conn), 0)

    def test_rollback_ante_error(self):
        with self.assertRaises(db.ErrorSimulado):
            db.registrar_venta(self.conn, self.pid, 3, simular_error=True)
        self.assertEqual(db.obtener_producto(self.conn, self.pid)["cantidad"], 10)
        self.assertEqual(db.contar_ventas(self.conn), 0)

    def test_no_eliminar_con_ventas(self):
        db.registrar_venta(self.conn, self.pid, 1)
        with self.assertRaises(db.ErrorNegocio):
            db.eliminar_producto(self.conn, self.pid)

    def test_eliminar_sin_ventas(self):
        db.eliminar_producto(self.conn, self.pid)
        self.assertIsNone(db.obtener_producto(self.conn, self.pid))

    def test_historial_join(self):
        db.registrar_venta(self.conn, self.pid, 2)
        self.assertEqual(db.historial_ventas(self.conn)[0]["nombre"], "Resistencia 1k")


if __name__ == "__main__":
    unittest.main()
