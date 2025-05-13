# polleria-montiel/app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from models import db, Proveedor, LotePolloVivo
from datetime import datetime, timezone # Importar date aquí también

# Crear instancia de la aplicación Flask
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar SQLAlchemy con la app
db.init_app(app)


# --- PROCESADOR DE CONTEXTO PARA EL AÑO ACTUAL ---
@app.context_processor
def inject_current_datetime(): # Puedes cambiar el nombre de la función si quieres
    return {'current_datetime': datetime.now(timezone.utc)}



# --- RUTAS PRINCIPALES ---
@app.route('/')
def index():
    return render_template('index.html', title="Inicio - Pollería Montiel")


# --- RUTAS PARA PROVEEDORES ---
@app.route('/proveedores')
def listar_proveedores():
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    return render_template('pollo_vivo/listar_proveedores.html',
                           proveedores=proveedores,
                           title="Proveedores")


@app.route('/proveedores/registrar', methods=['GET', 'POST'])
def registrar_proveedor():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        contacto = request.form.get('contacto')
        datos_pago = request.form.get('datos_pago')

        if not nombre:
            flash('El nombre del proveedor es obligatorio.', 'danger')
        else:
            # Verificar si el proveedor ya existe
            existente = Proveedor.query.filter_by(nombre=nombre).first()
            if existente:
                flash(f'El proveedor "{nombre}" ya existe.', 'warning')
            else:
                nuevo_proveedor = Proveedor(nombre=nombre,
                                            contacto=contacto,
                                            datos_pago=datos_pago)
                db.session.add(nuevo_proveedor)
                try:
                    db.session.commit()
                    flash('Proveedor registrado exitosamente!', 'success')
                    return redirect(url_for('listar_proveedores'))
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error al registrar proveedor: {str(e)}', 'danger')

    return render_template('pollo_vivo/registrar_proveedor.html',
                           title="Registrar Proveedor")


# --- RUTAS PARA LOTES DE POLLO VIVO ---
@app.route('/lotes')
def listar_lotes():
    # Unir LotePolloVivo con Proveedor para poder ordenar por nombre de proveedor y acceder fácilmente
    lotes = db.session.query(LotePolloVivo, Proveedor.nombre.label("nombre_proveedor"))\
                      .join(Proveedor, LotePolloVivo.proveedor_id == Proveedor.id)\
                      .order_by(LotePolloVivo.fecha_llegada.desc()).all()

    # los lotes ahora serán tuplas (objeto_lote, nombre_proveedor)
    return render_template(
        'pollo_vivo/listar_lotes.html',
        lotes_data=lotes,  # Cambiado el nombre de la variable para claridad
        title="Lotes de Pollo Vivo")


@app.route('/lotes/registrar', methods=['GET', 'POST'])
def registrar_lote():
    proveedores = Proveedor.query.order_by(
        Proveedor.nombre).all()  # Para el <select>

    if request.method == 'POST':
        try:
            fecha_llegada_str = request.form.get('fecha_llegada')
            proveedor_id = request.form.get('proveedor_id')
            marca_pollo = request.form.get('marca_pollo')
            cantidad_str = request.form.get('cantidad')
            tamano_promedio_kg_str = request.form.get('tamano_promedio_kg')
            precio_compra_kg_str = request.form.get('precio_compra_kg')

            pagado = 'pagado' in request.form  # Checkbox
            fecha_pago_str = request.form.get('fecha_pago')
            transporte_por_proveedor = 'transporte_por_proveedor' in request.form  # Checkbox
            observaciones = request.form.get('observaciones')

            # Validaciones básicas
            if not fecha_llegada_str or not proveedor_id or not cantidad_str or \
               not tamano_promedio_kg_str or not precio_compra_kg_str:
                flash('Todos los campos marcados con * son obligatorios.',
                      'danger')
                return render_template(
                    'pollo_vivo/registrar_lote.html',
                    proveedores=proveedores,
                    title="Registrar Lote",
                    form_data=request.form)  # Para rellenar el form

            # Conversiones
            fecha_llegada = datetime.strptime(fecha_llegada_str,
                                              '%Y-%m-%d').date()
            cantidad = int(cantidad_str)
            # Permitir 3 decimales para tamaño promedio, redondear el input
            tamano_promedio_kg = round(float(tamano_promedio_kg_str), 3)
            # Permitir 2 decimales para precio, redondear el input
            precio_compra_kg = round(float(precio_compra_kg_str), 2)

            fecha_pago = datetime.strptime(
                fecha_pago_str, '%Y-%m-%d').date() if fecha_pago_str else None

            nuevo_lote = LotePolloVivo(
                fecha_llegada=fecha_llegada,
                proveedor_id=int(proveedor_id),
                marca_pollo=marca_pollo,
                cantidad=cantidad,
                tamano_promedio_kg=tamano_promedio_kg,
                precio_compra_kg=precio_compra_kg,
                pagado=pagado,
                fecha_pago=fecha_pago,
                transporte_por_proveedor=transporte_por_proveedor,
                observaciones=observaciones)
            nuevo_lote.calcular_y_asignar_costo_total(
            )  # Calcular y asignar costo

            db.session.add(nuevo_lote)
            db.session.commit()
            flash('Lote de pollo vivo registrado exitosamente!', 'success')
            return redirect(url_for('listar_lotes'))

        except ValueError as ve:
            db.session.rollback()
            flash(
                f'Error en los datos ingresados. Verifica números y fechas: {str(ve)}',
                'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error inesperado: {str(e)}', 'danger')

        return render_template(
            'pollo_vivo/registrar_lote.html',
            proveedores=proveedores,
            title="Registrar Lote",
            form_data=request.form)  # Para rellenar el form en caso de error

    return render_template('pollo_vivo/registrar_lote.html',
                           proveedores=proveedores,
                           title="Registrar Lote")


# --- CREAR TABLAS Y EJECUTAR APP ---
def create_tables():
    with app.app_context():
        db.create_all()
    print("Tablas creadas (si no existían).")


if __name__ == '__main__':
    create_tables(
    )  # Llama a esta función para asegurar que las tablas estén creadas
    app.run(host='0.0.0.0', port=5000, debug=True)
