# polleria-montiel/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date # Asegúrate de importar date

db = SQLAlchemy()

                # Definición de modelos para Pollo Vivo
class Proveedor(db.Model):
    __tablename__ = 'proveedor' # Buena práctica definir el nombre de la tabla explícitamente
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    contacto = db.Column(db.String(50), nullable=True) # Teléfono o WhatsApp
    datos_pago = db.Column(db.String(200), nullable=True) # No. cuenta/CLABE, banco
    
    # Relación: Un proveedor puede tener muchos lotes
    lotes = db.relationship('LotePolloVivo', backref='proveedor_rel', lazy=True) # Cambiado backref para evitar colisión

    def __repr__(self):
        return f'<Proveedor {self.id}: {self.nombre}>'

class LotePolloVivo(db.Model):
    __tablename__ = 'lote_pollo_vivo'
    id = db.Column(db.Integer, primary_key=True)
    fecha_llegada = db.Column(db.Date, nullable=False, default=date.today) # Usar date.today para el default
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), nullable=False)
    marca_pollo = db.Column(db.String(50), nullable=True)
    cantidad = db.Column(db.Integer, nullable=False) # Piezas totales
    tamano_promedio_kg = db.Column(db.Float, nullable=False) # Promedio en kg
    precio_compra_kg = db.Column(db.Float, nullable=False) # Hasta 2 decimales
    costo_total_lote = db.Column(db.Float, nullable=True) # Calculado

    # Campos adicionales de tu conceptualización
    pagado = db.Column(db.Boolean, default=False)
    fecha_pago = db.Column(db.Date, nullable=True)
    transporte_por_proveedor = db.Column(db.Boolean, default=True)
    observaciones = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Lote {self.id} - Marca: {self.marca_pollo} - Fecha: {self.fecha_llegada}>'

    # Método para calcular el costo total del lote
    def calcular_y_asignar_costo_total(self):
        if self.tamano_promedio_kg is not None and self.cantidad is not None and self.precio_compra_kg is not None:
            total_kg_carga = self.tamano_promedio_kg * self.cantidad
            costo_calculado = total_kg_carga * self.precio_compra_kg
            self.costo_total_lote = round(costo_calculado) # Redondeado a entero
        else:
            self.costo_total_lote = None

            #Definición de modelos para Pollo Vivo

