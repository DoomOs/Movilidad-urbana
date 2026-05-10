"""
Modelos SQLAlchemy para el sistema de movilidad urbana.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base


class NivelTrafico(str, enum.Enum):
    BAJO = "Bajo"
    MEDIO = "Medio"
    ALTO = "Alto"
    MUY_ALTO = "Muy Alto"


class CondicionClima(str, enum.Enum):
    DESPEJADO = "Despejado"
    NUBLADO = "Nublado"
    LLUVIA_LIGERA = "Lluvia Ligera"
    LLUVIA_INTENSA = "Lluvia Intensa"


class TipoVehiculo(str, enum.Enum):
    AUTOMOVIL = "automovil"
    BICICLETA = "bicicleta"
    MOTOCICLETA = "motocicleta"
    AUTOBUS = "autobus"
    CAMION = "camion"


class DiaSemana(str, enum.Enum):
    LUNES = "Lunes"
    MARTES = "Martes"
    MIERCOLES = "Miércoles"
    JUEVES = "Jueves"
    VIERNES = "Viernes"
    SABADO = "Sábado"
    DOMINGO = "Domingo"


class Ciudad(Base):
    """Modelo para ciudades de Guatemala."""
    __tablename__ = "ciudades"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False, index=True)
    departamento = Column(String(100), nullable=False)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    calles = relationship("Calle", back_populates="ciudad", cascade="all, delete-orphan")
    registros = relationship("RegistroTrafico", back_populates="ciudad")


class Calle(Base):
    """Modelo para calles/avenidas dentro de una ciudad."""
    __tablename__ = "calles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    ciudad_id = Column(Integer, ForeignKey("ciudades.id"), nullable=False)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    tipo = Column(String(50), default="avenida")  # avenida, calle, boulevard
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    ciudad = relationship("Ciudad", back_populates="calles")
    origen_registros = relationship("RegistroTrafico", foreign_keys="RegistroTrafico.origen_id", back_populates="origen")
    destino_registros = relationship("RegistroTrafico", foreign_keys="RegistroTrafico.destino_id", back_populates="destino")
    nodos_origen = relationship("Nodo", foreign_keys="Nodo.calle_origen_id", back_populates="calle_origen")
    nodos_destino = relationship("Nodo", foreign_keys="Nodo.calle_destino_id", back_populates="calle_destino")


class RegistroTrafico(Base):
    """Modelo para registros de tráfico en el dataset."""
    __tablename__ = "registros_trafico"

    id = Column(Integer, primary_key=True, index=True)
    ciudad_id = Column(Integer, ForeignKey("ciudades.id"), nullable=False)
    origen_id = Column(Integer, ForeignKey("calles.id"), nullable=False)
    destino_id = Column(Integer, ForeignKey("calles.id"), nullable=False)
    distancia_km = Column(Float, nullable=False)
    trafico = Column(SQLEnum(NivelTrafico), default=NivelTrafico.MEDIO)
    clima = Column(SQLEnum(CondicionClima), default=CondicionClima.DESPEJADO)
    hora = Column(Integer, default=12)  # 0-23
    dia_semana = Column(SQLEnum(DiaSemana), default=DiaSemana.LUNES)
    tiempo_estimado_min = Column(Float, nullable=False)
    vehiculo = Column(SQLEnum(TipoVehiculo), default=TipoVehiculo.AUTOMOVIL)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    ciudad = relationship("Ciudad", back_populates="registros")
    origen = relationship("Calle", foreign_keys=[origen_id], back_populates="origen_registros")
    destino = relationship("Calle", foreign_keys=[destino_id], back_populates="destino_registros")


class Nodo(Base):
    """Modelo para nodos del grafo de rutas."""
    __tablename__ = "nodas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False, index=True)
    ciudad_id = Column(Integer, ForeignKey("ciudades.id"), nullable=False)
    calle_origen_id = Column(Integer, ForeignKey("calles.id"), nullable=True)
    calle_destino_id = Column(Integer, ForeignKey("calles.id"), nullable=True)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    ciudad = relationship("Ciudad")
    calle_origen = relationship("Calle", foreign_keys=[calle_origen_id], back_populates="nodos_origen")
    calle_destino = relationship("Calle", foreign_keys=[calle_destino_id], back_populates="nodos_destino")
    aristas_from = relationship("Arista", foreign_keys="Arista.nodo_origen_id", back_populates="nodo_origen", cascade="all, delete-orphan")
    aristas_to = relationship("Arista", foreign_keys="Arista.nodo_destino_id", back_populates="nodo_destino")


class Arista(Base):
    """Modelo para aristas (conexiones entre nodos)."""
    __tablename__ = "aristas"

    id = Column(Integer, primary_key=True, index=True)
    nodo_origen_id = Column(Integer, ForeignKey("nodas.id"), nullable=False)
    nodo_destino_id = Column(Integer, ForeignKey("nodas.id"), nullable=False)
    distancia_km = Column(Float, nullable=False)
    tiempo_min = Column(Float, nullable=False)
    trafico = Column(SQLEnum(NivelTrafico), default=NivelTrafico.MEDIO)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    nodo_origen = relationship("Nodo", foreign_keys=[nodo_origen_id], back_populates="aristas_from")
    nodo_destino = relationship("Nodo", foreign_keys=[nodo_destino_id], back_populates="aristas_to")


class BusquedaHistorial(Base):
    """Modelo para historial de búsquedas."""
    __tablename__ = "busqueda_historial"

    id = Column(Integer, primary_key=True, index=True)
    ciudad = Column(String(100), nullable=False)
    origen = Column(String(200), nullable=False)
    destino = Column(String(200), nullable=False)
    hora = Column(Integer, default=12)
    dia_semana = Column(String(20), default="Lunes")
    vehiculo = Column(String(50), default="automovil")
    clima = Column(String(50), default="Despejado")
    resultado_json = Column(String(5000), nullable=True)
    mejor_algoritmo = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ModeloML(Base):
    """Modelo para guardar info de modelos ML entrenados."""
    __tablename__ = "modelos_ml"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    tipo = Column(String(50), nullable=False)  # regresion, random_forest, xgboost
    archivo = Column(String(200), nullable=True)
    metricas_json = Column(String(1000), nullable=True)
    r2_score = Column(Float, default=0.0)
    mae = Column(Float, default=0.0)
    rmse = Column(Float, default=0.0)
    activo = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)