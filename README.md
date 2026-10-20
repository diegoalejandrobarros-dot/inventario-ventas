# Sistema de inventario y ventas (Python + SQLite)

Parcial práctico — **Acceso a Datos 2026**. Aplicación de consola para una tienda de componentes
electrónicos que administra productos y registra ventas **sin dejar el inventario inconsistente**,
gracias al uso de transacciones (`commit()` / `rollback()`).

## Requisitos
- Python 3.8 o superior (solo usa la librería estándar: `sqlite3`). No hay que instalar nada.

## Cómo ejecutarlo
```bash
git clone <https://github.com/diegoalejandrobarros-dot/inventario-ventas.git>
cd inventario-ventas

python app.py            # aplicación con menú interactivo
python demo_rollback.py  # demostración del reto de rollback
python tests/test_inventario.py -v   # pruebas automáticas
```
La base de datos `tienda.db` y sus tablas se crean automáticamente al primer arranque.

## Funcionalidades
| Opción | Descripción |
|---|---|
| 1 | Registrar producto (nombre, precio, cantidad) |
| 2 | Consultar todos los productos |
| 3 | Actualizar precio o cantidad |
| 4 | Eliminar producto (se bloquea si tiene ventas: integridad referencial) |
| 5 | Registrar venta (validada y transaccional) |
| 6 | Historial de ventas con nombre del producto (`JOIN`) |
| 7 | Demostrar rollback con un error controlado |

Todas las consultas usan parámetros `?` (sin concatenar strings → sin inyección SQL).

## Estructura
```
app.py                  Menú interactivo (interfaz de consola)
db.py                   Acceso a datos: esquema, CRUD y transacción de venta
demo_rollback.py        Demostración del error controlado + rollback
tests/                  Pruebas unitarias (unittest)
docs/ANALISIS.md        Análisis y diseño (Parte 1), arquitectura y transacción
evidencias/             Pantallazos de ejecución
```

## Documentación
- [Análisis, modelo de datos, arquitectura y transacción](docs/ANALISIS.md)

## Evidencias de ejecución
| | |
|---|---|
| Registro y consulta | ![](evidencias/01_registro_y_consulta.png) |
| Actualizar, vender e historial (JOIN) | ![](evidencias/02_actualizar_venta_historial.png) |
| Validaciones de la venta | ![](evidencias/03_validaciones_venta.png) |
| Eliminar respetando la FK | ![](evidencias/04_eliminar_integridad.png) |
| Rollback desde el menú | ![](evidencias/05_rollback_desde_menu.png) |
| Demo de rollback | ![](evidencias/06_demo_rollback.png) |
| Pruebas unitarias | ![](evidencias/07_pruebas_unitarias.png) |
