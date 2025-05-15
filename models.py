# polleria-montiel/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timezone  # Asegúrate de importar date

db = SQLAlchemy()


# Definición de modelos para Proveedor en Pollo Vivo
class Proveedor(db.Model):
    __tablename__ = 'proveedor'  # Buena práctica definir el nombre de la tabla explícitamente
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    contacto = db.Column(db.String(50), nullable=True)  # Teléfono o WhatsApp
    datos_pago = db.Column(db.String(200),
                           nullable=True)  # No. cuenta/CLABE, banco
    # --- ELIMINACIÓN LÓGICA ---
    activo = db.Column(db.Boolean, default=True, nullable=False) 

    # Relación: Un proveedor puede tener muchos lotes
    lotes = db.relationship('LotePolloVivo',
                            backref='proveedor_rel',
                            lazy=True)  # Cambiado backref para evitar colisión

    def __repr__(self):
        return f'<Proveedor {self.id}: {self.nombre} (Activo: {self.activo})>'

# ... (Modelo Producto ajustado) ...
class Producto(db.Model):
    __tablename__ = 'producto'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    id_interno = db.Column(db.String(20), nullable=False, unique=True)
    categoria = db.Column(db.String(50),
                          nullable=False,
                          default="Pieza Despiece")
    porcentaje_distribucion_peso = db.Column(db.Float, nullable=True)
    porcentaje_distribucion_costo = db.Column(db.Float, nullable=True)
    cantidad_por_despiece = db.Column(db.Integer, nullable=False, default=1)
    costo_kg_referencia = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<Producto {self.id}: {self.nombre} ({self.id_interno})>'


#modelo deprecado
#class LotePolloVivo(db.Model):
#__tablename__ = 'lote_pollo_vivo'
#id = db.Column(db.Integer, primary_key=True)
#fecha_llegada = db.Column(db.Date, nullable=False, default=date.today) # Usar date.today para el default
#proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), nullable=False)
#marca_pollo = db.Column(db.String(50), nullable=True)
#cantidad = db.Column(db.Integer, nullable=False) # Piezas totales
#tamano_promedio_kg = db.Column(db.Float, nullable=False) # Promedio en kg
#precio_compra_kg = db.Column(db.Float, nullable=False) # Hasta 2 decimales
#costo_total_lote = db.Column(db.Float, nullable=True) # Calculado

# Campos adicionales de tu conceptualización
#pagado = db.Column(db.Boolean, default=False)
#fecha_pago = db.Column(db.Date, nullable=True)
#transporte_por_proveedor = db.Column(db.Boolean, default=True)
#observaciones = db.Column(db.Text, nullable=True)

#def __repr__(self):
#return f'<Lote {self.id} - Marca: {self.marca_pollo} - Fecha: {self.fecha_llegada}>'

# Método para calcular el costo total del lote
#def calcular_y_asignar_costo_total(self):
#if self.tamano_promedio_kg is not None and self.cantidad is not None and self.precio_compra_kg is not None:
#total_kg_carga = self.tamano_promedio_kg * self.cantidad
#costo_calculado = total_kg_carga * self.precio_compra_kg
#self.costo_total_lote = round(costo_calculado) # Redondeado a entero
#else:
#self.costo_total_lote = None


# ... (Modelo LotePolloVivo con relación añadida) ...
class LotePolloVivo(db.Model):
    __tablename__ = 'lote_pollo_vivo'
    id = db.Column(db.Integer, primary_key=True)
    fecha_llegada = db.Column(db.Date, nullable=False, default=date.today)
    proveedor_id = db.Column(db.Integer,
                             db.ForeignKey('proveedor.id'),
                             nullable=False)
    marca_pollo = db.Column(db.String(50), nullable=True)
    cantidad = db.Column(db.Integer, nullable=False)
    tamano_promedio_kg = db.Column(db.Float, nullable=False)
    precio_compra_kg = db.Column(db.Float, nullable=False)
    costo_total_lote = db.Column(db.Float,
                                 nullable=True)  # Calculado al guardar lote
    pagado = db.Column(db.Boolean, default=False)
    fecha_pago = db.Column(db.Date, nullable=True)
    transporte_por_proveedor = db.Column(db.Boolean, default=True)
    observaciones = db.Column(db.Text, nullable=True)

    # --- NUEVA RELACIÓN (UNO-A-UNO) CON CalculoCostosLote ---
    # backref='lote_origen' permite acceder al LotePolloVivo desde CalculoCostosLote
    # uselist=False indica que es una relación uno-a-uno (un lote tiene un cálculo)
    # cascade="all, delete-orphan" significa que si borras un LotePolloVivo,
    # también se borrará su CalculoCostosLote asociado.
    calculo_costos = db.relationship('CalculoCostosLote',
                                     backref='lote_origen',
                                     uselist=False,
                                     lazy='joined',
                                     cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Lote {self.id} - Marca: {self.marca_pollo} - Fecha: {self.fecha_llegada}>'

    def calcular_y_asignar_costo_total(
            self):  # Este calcula solo el costo total del lote inicial
        if self.tamano_promedio_kg is not None and self.cantidad is not None and self.precio_compra_kg is not None:
            total_kg_carga = self.tamano_promedio_kg * self.cantidad
            costo_calculado = total_kg_carga * self.precio_compra_kg
            self.costo_total_lote = round(costo_calculado)
        else:
            self.costo_total_lote = None


# --- NUEVO MODELO: CalculoCostosLote ---
class CalculoCostosLote(db.Model):
    __tablename__ = 'calculo_costos_lote'
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea a LotePolloVivo (relación uno-a-uno)
    lote_pollo_vivo_id = db.Column(db.Integer,
                                   db.ForeignKey('lote_pollo_vivo.id'),
                                   unique=True,
                                   nullable=False)

    fecha_calculo = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc))  # Fecha/Hora del cálculo

    # Datos del lote original en el momento del cálculo (para referencia histórica)
    pv_lote_original_kg = db.Column(db.Float, nullable=False)
    tpv_lote_original_kg = db.Column(db.Float, nullable=False)

    # Resultados del cálculo del pollo procesado
    pv_g_calculado = db.Column(db.Float,
                               nullable=False)  # $pv + transporte ajustado
    tpv_m_calculado_kg = db.Column(
        db.Float, nullable=False)  # Peso promedio después de merma
    valor_total_procesado_calculado_por_pollo = db.Column(
        db.Float, nullable=False)  # Costo total de procesar un pollo
    costo_kg_pollo_entero_procesado_calculado = db.Column(
        db.Float, nullable=False)  # $/kg_PM

    # --- NUEVA RELACIÓN (UNO-A-MUCHOS) CON DetalleCostoPiezaLote ---
    # backref='calculo_padre' permite acceder al CalculoCostosLote desde DetalleCostoPiezaLote
    # cascade="all, delete-orphan" significa que si borras un CalculoCostosLote,
    # también se borrarán todos sus DetalleCostoPiezaLote asociados.
    detalles_costos_piezas = db.relationship('DetalleCostoPiezaLote',
                                             backref='calculo_padre',
                                             lazy='dynamic',
                                             cascade="all, delete-orphan")

    def __repr__(self):
        return f'<CalculoCostosLote {self.id} para Lote {self.lote_pollo_vivo_id}>'


# --- NUEVO MODELO: DetalleCostoPiezaLote ---
class DetalleCostoPiezaLote(db.Model):
    __tablename__ = 'detalle_costo_pieza_lote'
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea al cálculo padre
    calculo_costos_lote_id = db.Column(db.Integer,
                                       db.ForeignKey('calculo_costos_lote.id'),
                                       nullable=False)

    # Clave foránea al producto (pieza)
    producto_id = db.Column(db.Integer,
                            db.ForeignKey('producto.id'),
                            nullable=False)

    # Resultados del cálculo para esta pieza específica en este lote
    peso_estimado_pieza_calculado_kg = db.Column(db.Float, nullable=False)
    costo_total_pieza_calculado = db.Column(db.Float, nullable=False)
    costo_kg_pieza_calculado = db.Column(db.Float,
                                         nullable=False)  # costo_kg_derivado

    # Relación para acceder fácilmente al objeto Producto desde aquí (opcional pero útil)
    producto = db.relationship('Producto', lazy='joined')

    def __repr__(self):
        return f'<DetalleCostoPieza {self.id} - ProductoID: {self.producto_id} para CalculoID: {self.calculo_costos_lote_id}>'
