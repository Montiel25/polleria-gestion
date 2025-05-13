from app import app, db  # Importa la instancia de la app y db desde tu archivo app.py
from models import Producto  # Importa tu modelo Producto

# Datos de los productos base
# Id_interno, Nombre, %_dist_peso (para una unidad), %_dist_costo (para una unidad), cantidad_despiece, categoria
# Los porcentajes de distribución de costo para las piezas (cbz a mlj_hgd),
# cuando se multiplican por su 'cantidad_por_despiece' y se suman, deben dar 1.0 (o 100%).
# Verificación:
# (0.01*1) + (0.04*1) + (0.06*2) + (0.50*1) + (0.045*1) + (0.125*2) + (0.01*2) + (0.015*1)
# = 0.01 + 0.04 + 0.12 + 0.50 + 0.045 + 0.25 + 0.02 + 0.015 = 1.00 (100%) ¡Correcto!
productos_base_data = [
    # 'Pollo Entero Procesado' es una referencia, sus porcentajes se refieren al 100% de sí mismo.
    {
        'id_interno': 'pe',
        'nombre': 'Pollo Entero Procesado',
        'porcentaje_distribucion_peso': 1.0,
        'porcentaje_distribucion_costo': 1.0,
        'cantidad_por_despiece': 1,
        'categoria': 'Pieza Despiece',
        'costo_kg_referencia': None
    },

    # Piezas del despiece
    {
        'id_interno': 'cbz',
        'nombre': 'Cabeza',
        'porcentaje_distribucion_peso': 0.03,
        'porcentaje_distribucion_costo': 0.01,
        'cantidad_por_despiece': 1,
        'categoria': 'Pieza Despiece',
        'costo_kg_referencia': None
    },
    {
        'id_interno': 'h',
        'nombre': 'Huacal',
        'porcentaje_distribucion_peso': 0.07,
        'porcentaje_distribucion_costo': 0.04,
        'cantidad_por_despiece': 1,
        'categoria': 'Pieza Despiece',
        'costo_kg_referencia': None
    },
    {
        'id_interno': 'al',
        'nombre': 'Alas',
        'porcentaje_distribucion_peso': 0.045,
        'porcentaje_distribucion_costo': 0.06,
        'cantidad_por_despiece': 2,
        'categoria': 'Pieza Despiece',
        'costo_kg_referencia': None
    },
    {
        'id_interno': 'pech',
        'nombre': 'Pechuga',
        'porcentaje_distribucion_peso': 0.35,
        'porcentaje_distribucion_costo': 0.50,
        'cantidad_por_despiece': 1,
        'categoria': 'Pieza Despiece',
        'costo_kg_referencia': None
    },
    {
        'id_interno': 'cd',
        'nombre': 'Cadera',
        'porcentaje_distribucion_peso': 0.08,
        'porcentaje_distribucion_costo': 0.045,
        'cantidad_por_despiece': 1,
        'categoria': 'Pieza Despiece',
        'costo_kg_referencia': None
    },
    {
        'id_interno': 'pm',
        'nombre': 'Pernil(es)',
        'porcentaje_distribucion_peso': 0.15,
        'porcentaje_distribucion_costo': 0.125,
        'cantidad_por_despiece': 2,
        'categoria': 'Pieza Despiece',
        'costo_kg_referencia': None
    },
    {
        'id_interno': 'pt',
        'nombre': 'Patas',
        'porcentaje_distribucion_peso': 0.015,
        'porcentaje_distribucion_costo': 0.01,  # Costo corregido a 1% por pata
        'cantidad_por_despiece': 2,
        'categoria': 'Pieza Despiece',
        'costo_kg_referencia': None
    },
    {
        'id_interno': 'mlj_hgd',
        'nombre': 'Molleja con Higado',
        'porcentaje_distribucion_peso': 0.05,
        'porcentaje_distribucion_costo': 0.015,
        'cantidad_por_despiece': 1,
        'categoria': 'Pieza Despiece',
        'costo_kg_referencia': None
    },
]


def seed_data():
    with app.app_context(
    ):  # Necesario para operaciones de BD fuera de una request de Flask
        print("Verificando y añadiendo/actualizando productos base...")
        for prod_data in productos_base_data:
            existente = Producto.query.filter_by(
                id_interno=prod_data['id_interno']).first()

            # Preparar los datos para el producto
            datos_producto_actual = {
                'id_interno':
                prod_data['id_interno'],
                'nombre':
                prod_data['nombre'],
                'categoria':
                prod_data['categoria'],
                'porcentaje_distribucion_peso':
                prod_data['porcentaje_distribucion_peso'],
                'porcentaje_distribucion_costo':
                prod_data['porcentaje_distribucion_costo'],
                'cantidad_por_despiece':
                prod_data['cantidad_por_despiece'],
                'costo_kg_referencia':
                prod_data.get('costo_kg_referencia'
                              )  # Usar .get() para el campo opcional
            }

            if not existente:
                nuevo_producto = Producto(**datos_producto_actual)
                db.session.add(nuevo_producto)
                print(f"Añadiendo: {datos_producto_actual['nombre']}")
            else:
                # Actualizar el producto existente si algún dato ha cambiado
                actualizar = False
                for campo, valor in datos_producto_actual.items():
                    if getattr(existente, campo) != valor:
                        setattr(existente, campo, valor)
                        actualizar = True

                if actualizar:
                    print(f"Actualizando: {datos_producto_actual['nombre']}")
                else:
                    print(
                        f"Ya existe y coincide: {datos_producto_actual['nombre']}"
                    )

        try:
            db.session.commit()
            print(
                "Productos base verificados/actualizados en la base de datos.")
        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar productos base: {e}")


if __name__ == '__main__':
    seed_data()
