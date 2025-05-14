# polleria-montiel/app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from models import db, Proveedor, LotePolloVivo, Producto, CalculoCostosLote, DetalleCostoPiezaLote  # Importar todos los modelos
from datetime import datetime, timezone  # Importar date aquí también

# Crear instancia de la aplicación Flask
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar SQLAlchemy con la app
db.init_app(app)


# --- PROCESADOR DE CONTEXTO PARA EL AÑO ACTUAL ---
@app.context_processor
def inject_current_datetime(
):  # Puedes cambiar el nombre de la función si quieres
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


# --- RUTA PARA ELIMINAR UN PROVEEDOR ---
@app.route('/proveedores/eliminar/<int:proveedor_id>', methods=['POST'])
def eliminar_proveedor(proveedor_id):
    proveedor_a_eliminar = Proveedor.query.get_or_404(proveedor_id)

    # Validación adicional (opcional pero recomendada):
    # Verificar si el proveedor tiene lotes asociados antes de eliminar.
    if proveedor_a_eliminar.lotes:  # Si la lista lote_pollo_vivo no está vacía
        flash(
            f'No se puede eliminar el proveedor "{proveedor_a_eliminar.nombre}" porque tiene lotes de pollo vivo asociados. Primero elimina o reasigna esos lotes.',
            'danger')
        return redirect(url_for('listar_proveedores'))

    try:
        nombre_proveedor_eliminado = proveedor_a_eliminar.nombre  # Guardar nombre para el mensaje flash
        db.session.delete(proveedor_a_eliminar)
        db.session.commit()
        flash(
            f'Proveedor "{nombre_proveedor_eliminado}" eliminado exitosamente.',
            'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el proveedor: {str(e)}', 'danger')

    return redirect(url_for('listar_proveedores'))


# --- RUTAS PARA LOTES DE POLLO VIVO ---
@app.route('/lotes')
def listar_lotes():
    # Unir LotePolloVivo con Proveedor para poder ordenar por nombre de proveedor y acceder fácilmente
    lotes = db.session.query(LotePolloVivo, Proveedor.nombre.label("nombre_proveedor"))\
                      .join(Proveedor, LotePolloVivo.proveedor_id == Proveedor.id)\
                      .order_by(LotePolloVivo.fecha_llegada.desc(), LotePolloVivo.id.desc()).all()

    # los lotes ahora serán tuplas (objeto_lote, nombre_proveedor)
    return render_template(
        'pollo_vivo/listar_lotes.html',
        lotes_data=lotes,  # Cambiado el nombre de la variable para claridad
        title="Lotes de Pollo Vivo")


# --- RUTA PARA VER COSTOS CALCULADOS DE UN LOTE ESPECÍFICO ---
@app.route('/lotes/<int:lote_id>/costos_calculados')
def ver_costos_lote(lote_id):
    lote = LotePolloVivo.query.get_or_404(
        lote_id)  # Obtiene el lote o devuelve un 404 si no existe

    # El acceso a lote.calculo_costos y lote.calculo_costos.detalles_costos_piezas
    # debería funcionar directamente debido a las relaciones y lazy='joined' / 'dynamic'
    # No es necesario hacer queries separadas aquí si las relaciones están bien definidas.

    if not lote.calculo_costos:
        flash(
            f'Aún no se han calculado los costos para el lote ID: {lote_id}.',
            'warning')
        # Podrías redirigir a listar_lotes o mostrar un mensaje simple
        return redirect(url_for('listar_lotes'))

    # Si usaste lazy='dynamic' para detalles_costos_piezas, necesitas .all() o similar para obtener la lista
    # Si usaste lazy='joined' o 'select', ya debería ser una lista (o None)
    # Con lazy='dynamic', detalles_costos_piezas es un objeto query.
    # Vamos a asumir que quieres todos los detalles:
    detalles_piezas = lote.calculo_costos.detalles_costos_piezas.all(
    ) if lote.calculo_costos.detalles_costos_piezas else []
    # Si hubieras usado lazy='joined' en la relación detalles_costos_piezas, sería:
    # detalles_piezas = lote.calculo_costos.detalles_costos_piezas if lote.calculo_costos.detalles_costos_piezas else []

    return render_template('pollo_vivo/ver_costos_lote.html',
                           lote=lote,
                           calculo_costos=lote.calculo_costos,
                           detalles_piezas=detalles_piezas,
                           title=f"Costos calculados - Carga {lote.id}")


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
            # --- LLAMAR A LA NUEVA FUNCIÓN DE CÁLCULO DE COSTOS ---
            exito_calculo, mensaje_calculo = calcular_y_guardar_costos_lote(
                nuevo_lote)
            if exito_calculo:
                flash(
                    f'Lote de pollo vivo registrado exitosamente! {mensaje_calculo}',
                    'success')
            else:
                # El lote se guardó, pero el cálculo de costos falló.
                # Podrías decidir si esto es un error crítico o solo una advertencia.
                flash(
                    f'Lote registrado, pero hubo un error en el cálculo de costos: {mensaje_calculo}',
                    'warning')

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
            form_data=request.form if request.method == 'POST'
            and not exito_calculo else None)  # Ajuste form_data
    return render_template('pollo_vivo/registrar_lote.html',
                           proveedores=proveedores,
                           title="Registrar Lote")


# --- FUNCIÓN PARA CALCULAR Y GUARDAR COSTOS DE UN LOTE ---
def calcular_y_guardar_costos_lote(lote_pollo_vivo_obj):
    """
    Calcula los costos de procesamiento para un LotePolloVivo y guarda los resultados.
    """
    try:
        print(
            f"Iniciando cálculo de costos para Lote ID: {lote_pollo_vivo_obj.id}"
        )

        # Variables y datos importantes del lote original
        pv = lote_pollo_vivo_obj.precio_compra_kg  # Precio del pollo vivo (costo base del ave)
        tpv = lote_pollo_vivo_obj.tamano_promedio_kg  # Tamaño del pollo vivo (peso en kg)

        # Constantes del negocio (puedes moverlas a config.py si cambian raramente)
        TRANSPORTE_PCT = 0.10
        TRANSPORTE_MIN = 4.50
        TRANSPORTE_MAX = 6.50

        GASTOS_OPERATIVOS_FIJOS = 20.00  # Electricidad + Mano de obra + Maquinaria

        MERMA_PCT = 0.22
        # Desglose de merma (informativo, no usado directamente en cálculo de tpv_m si ya tienes MERMA_PCT)
        # SANGRE_PCT = 0.06
        # VISCERAS_PCT = 0.09
        # PLUMAS_PCT = 0.07

        # 1. Calcular el precio del pollo con gastos de transporte ($pv_g)
        gasto_transporte_calculado = pv * TRANSPORTE_PCT
        gasto_transporte_ajustado = max(
            min(gasto_transporte_calculado, TRANSPORTE_MAX), TRANSPORTE_MIN)
        pv_g = pv + gasto_transporte_ajustado
        print(
            f"  pv: {pv}, gasto_transporte_ajustado: {gasto_transporte_ajustado}, pv_g: {pv_g}"
        )

        # 2. Calcular la merma total (merma_total)
        merma_total_kg = tpv * MERMA_PCT
        print(f"  tpv: {tpv}, merma_total_kg: {merma_total_kg}")

        # 3. Calcular el peso después de la merma (tpv_m)
        tpv_m_kg = tpv - merma_total_kg
        if tpv_m_kg <= 0:  # Validación importante
            raise ValueError(
                "El peso después de la merma (tpv_m) no puede ser cero o negativo."
            )
        print(f"  tpv_m_kg: {tpv_m_kg}")

        # 4. Gastos operativos (ya definidos como GASTOS_OPERATIVOS_FIJOS)
        gastos_operativos = GASTOS_OPERATIVOS_FIJOS
        print(f"  gastos_operativos: {gastos_operativos}")

        # 5. Calcular el valor total después del procesamiento (Valor_total por pollo)
        # Tu fórmula original es: ($pv_g × tpv_m) + gastos_operativos = Valor_total
        # Aquí $pv_g es el costo por kg del pollo vivo + transporte.
        # Entonces, el costo del pollo vivo (con transporte) para UN pollo de tamaño tpv es pv_g * tpv
        # Pero tu ejemplo usa pv_g (costo/kg) * tpv_m (peso procesado). Esto implica que
        # el costo del material perdido en la merma se absorbe en el costo del material restante.
        # Vamos a seguir tu fórmula tal cual:
        valor_total_procesado_por_pollo = (pv_g * tpv_m_kg) + gastos_operativos
        print(
            f"  valor_total_procesado_por_pollo: {valor_total_procesado_por_pollo}"
        )

        # 6. Calcular el precio por kg procesado ($/kg_PM)
        costo_kg_pollo_entero_procesado = valor_total_procesado_por_pollo / tpv_m_kg
        print(
            f"  costo_kg_pollo_entero_procesado: {costo_kg_pollo_entero_procesado}"
        )

        # Crear y guardar el registro de CalculoCostosLote
        # Verificar si ya existe un cálculo para este lote (en caso de re-cálculo)
        calculo_existente = CalculoCostosLote.query.filter_by(
            lote_pollo_vivo_id=lote_pollo_vivo_obj.id).first()
        if calculo_existente:
            # Si existe, lo actualizamos (o podrías decidir borrarlo y crear uno nuevo)
            print(
                f"  Actualizando cálculo existente ID: {calculo_existente.id}")
            calculo_lote = calculo_existente
            calculo_lote.fecha_calculo = datetime.now(
                timezone.utc)  # Actualizar fecha
            # Borrar detalles de piezas anteriores para este cálculo, para evitar duplicados
            DetalleCostoPiezaLote.query.filter_by(
                calculo_costos_lote_id=calculo_lote.id).delete()
        else:
            print("  Creando nuevo registro de CalculoCostosLote.")
            calculo_lote = CalculoCostosLote(
                lote_pollo_vivo_id=lote_pollo_vivo_obj.id)

        calculo_lote.pv_lote_original_kg = pv
        calculo_lote.tpv_lote_original_kg = tpv
        calculo_lote.pv_g_calculado = round(
            pv_g, 4)  # Redondear a 4 decimales para precisión intermedia
        calculo_lote.tpv_m_calculado_kg = round(tpv_m_kg, 4)
        calculo_lote.valor_total_procesado_calculado_por_pollo = round(
            valor_total_procesado_por_pollo, 4)
        calculo_lote.costo_kg_pollo_entero_procesado_calculado = round(
            costo_kg_pollo_entero_procesado, 4)

        if not calculo_existente:  # Solo añadir si es nuevo
            db.session.add(calculo_lote)

        # Es importante hacer commit aquí para que calculo_lote obtenga un ID si es nuevo,
        # necesario para los detalles de las piezas.
        db.session.commit()
        print(
            f"  CalculoCostosLote ID: {calculo_lote.id} guardado/actualizado.")

        # Calcular y guardar el costo de cada pieza ("Pieza Despiece")
        productos_despiece = Producto.query.filter_by(
            categoria="Pieza Despiece").all()

        # El producto 'pe' (Pollo Entero Procesado) es especial. Su costo_kg ya lo tenemos.
        # Lo trataremos como un detalle más para consistencia.

        print("  Calculando detalles de costos por pieza:")
        for producto_pieza in productos_despiece:
            if producto_pieza.id_interno == 'pe':  # Caso especial Pollo Entero Procesado
                peso_estimado_pieza = tpv_m_kg  # Su peso es el total del pollo procesado
                costo_total_pieza = valor_total_procesado_por_pollo  # Su costo es el total del pollo procesado
                costo_kg_pieza = costo_kg_pollo_entero_procesado
            else:
                # Fórmula para peso: tpv_m * %_dist_peso_unidad * cantidad_despiece
                peso_estimado_pieza = tpv_m_kg * producto_pieza.porcentaje_distribucion_peso * producto_pieza.cantidad_por_despiece

                # Fórmula para costo: Valor_total_pollo * %_dist_costo_unidad * cantidad_despiece
                costo_total_pieza = valor_total_procesado_por_pollo * producto_pieza.porcentaje_distribucion_costo * producto_pieza.cantidad_por_despiece

                if peso_estimado_pieza == 0:  # Evitar división por cero
                    costo_kg_pieza = 0
                    print(
                        f"    Advertencia: Peso estimado para {producto_pieza.nombre} es 0. Costo/kg será 0."
                    )
                else:
                    costo_kg_pieza = costo_total_pieza / peso_estimado_pieza

            print(
                f"    {producto_pieza.nombre} ({producto_pieza.id_interno}): Peso Est: {round(peso_estimado_pieza,4)} kg, Costo Total: ${round(costo_total_pieza,4)}, Costo/kg: ${round(costo_kg_pieza,4)}"
            )

            detalle_costo = DetalleCostoPiezaLote(
                calculo_costos_lote_id=calculo_lote.id,
                producto_id=producto_pieza.id,
                peso_estimado_pieza_calculado_kg=round(peso_estimado_pieza, 4),
                costo_total_pieza_calculado=round(costo_total_pieza, 4),
                costo_kg_pieza_calculado=round(costo_kg_pieza,
                                               4)  # El costo_kg_derivado
            )
            db.session.add(detalle_costo)

        db.session.commit()
        print(
            f"Cálculo de costos para Lote ID: {lote_pollo_vivo_obj.id} completado y guardado."
        )
        return True, "Costos calculados y guardados exitosamente."

    except ValueError as ve:  # Errores de datos, ej. tpv_m_kg <= 0
        db.session.rollback()
        print(
            f"Error de valor en cálculo de costos para Lote ID {lote_pollo_vivo_obj.id}: {str(ve)}"
        )
        return False, f"Error de valor en el cálculo: {str(ve)}"
    except Exception as e:
        db.session.rollback()
        print(
            f"Error general en cálculo de costos para Lote ID {lote_pollo_vivo_obj.id}: {str(e)}"
        )
        # Podrías querer loggear el traceback completo aquí para depuración
        # import traceback
        # print(traceback.format_exc())
        return False, f"Error inesperado durante el cálculo de costos: {str(e)}"


# --- RUTA PARA ELIMINAR UN LOTE DE POLLO VIVO ---
@app.route('/lotes/eliminar/<int:lote_id>', methods=['POST'])
def eliminar_lote(lote_id):
    lote_a_eliminar = LotePolloVivo.query.get_or_404(lote_id)

    # Validación adicional (opcional):
    # Si en el futuro un LoteProcesado depende de LotePolloVivo,
    # deberías verificar aquí que no haya Lotes Procesados asociados.
    # Por ahora, la cascada se encargará de CalculoCostosLote y sus Detalles.

    try:
        # El 'calculo_costos' y sus 'detalles_costos_piezas' se borrarán en cascada
        # gracias a la configuración de `cascade="all, delete-orphan"` en las relaciones.
        db.session.delete(lote_a_eliminar)
        db.session.commit()
        flash(
            f'Lote ID: {lote_id} y sus costos asociados eliminados exitosamente.',
            'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el lote: {str(e)}', 'danger')

    return redirect(url_for('listar_lotes'))


# --- CREAR TABLAS Y EJECUTAR APP ---
def create_tables():
    with app.app_context():
        db.create_all()
    print("Tablas creadas (si no existían).")


if __name__ == '__main__':
    create_tables(
    )  # Llama a esta función para asegurar que las tablas estén creadas
    app.run(host='0.0.0.0', port=5000, debug=True)
