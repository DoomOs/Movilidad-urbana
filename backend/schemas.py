"""
Schemas Pydantic para validación de datos de entrada/salida.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class NivelTraficoEnum(str, Enum):
    BAJO = "Bajo"
    MEDIO = "Medio"
    ALTO = "Alto"
    MUY_ALTO = "Muy Alto"


class ClimaEnum(str, Enum):
    DESPEJADO = "Despejado"
    NUBLADO = "Nublado"
    LLUVIA_LIGERA = "Lluvia Ligera"
    LLUVIA_INTENSA = "Lluvia Intensa"


class VehiculoEnum(str, Enum):
    AUTOMOVIL = "automovil"
    BICICLETA = "bicicleta"
    MOTOCICLETA = "motocicleta"
    AUTOBUS = "autobus"
    CAMION = "camion"


class DiaSemanaEnum(str, Enum):
    LUNES = "Lunes"
    MARTES = "Martes"
    MIERCOLES = "Miércoles"
    JUEVES = "Jueves"
    VIERNES = "Viernes"
    SABADO = "Sábado"
    DOMINGO = "Domingo"


# ==================== Ciudad ====================
class CiudadBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    departamento: str = Field(..., min_length=1, max_length=100)


class CiudadResponse(CiudadBase):
    id: int
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    num_calles: Optional[int] = None

    class Config:
        from_attributes = True


# ==================== Calle ====================
class CalleBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    tipo: Optional[str] = "avenida"


class CalleResponse(CalleBase):
    id: int
    ciudad_id: int

    class Config:
        from_attributes = True


# ==================== Solicitud Ruta ====================
class SolicitudRuta(BaseModel):
    """Solicitud para buscar una ruta."""
    origen: str = Field(..., description="Nombre de la calle de origen")
    destino: str = Field(..., description="Nombre de la calle de destino")
    ciudad: Optional[str] = Field(None, description="Ciudad (opcional, usa la primera si no se especifica)")
    hora: int = Field(12, ge=0, le=23, description="Hora del día (0-23)")
    dia_semana: DiaSemanaEnum = Field(DiaSemanaEnum.LUNES, description="Día de la semana")
    tipo_vehiculo: VehiculoEnum = Field(VehiculoEnum.AUTOMOVIL, description="Tipo de vehículo")
    clima: ClimaEnum = Field(ClimaEnum.DESPEJADO, description="Condición climática")

    @field_validator('hora')
    @classmethod
    def validar_hora(cls, v):
        if not 0 <= v <= 23:
            raise ValueError('La hora debe estar entre 0 y 23')
        return v


# ==================== Resultado Ruta ====================
class ResultadoRuta(BaseModel):
    """Resultado de una búsqueda de ruta."""
    algoritmo: str
    ruta: List[str]
    distancia_total: float = Field(..., ge=0)
    tiempo_total: float = Field(..., ge=0)
    tiempo_ajustado: Optional[float] = None
    nodos_expandidos: int = Field(..., ge=0)
    recomendaciones: List[str] = []
    advertencias: List[str] = []
    coordenadas_ruta: Optional[List[Dict[str, float]]] = None

    class Config:
        from_attributes = True


class ComparacionAlgoritmos(BaseModel):
    """Comparación de los tres algoritmos."""
    bfs: Optional[Dict[str, Any]] = None
    dfs: Optional[Dict[str, Any]] = None
    a_estrella: Optional[Dict[str, Any]] = None
    mejor_opcion: str = ""
    razon: str = ""


# ==================== Predicción ML ====================
class SolicitudPrediccion(BaseModel):
    """Solicitud para predecir tiempo."""
    distancia_km: float = Field(..., gt=0, description="Distancia en kilómetros")
    nivel_trafico: NivelTraficoEnum = Field(..., description="Nivel de tráfico")
    hora: int = Field(12, ge=0, le=23, description="Hora del día")


class ResultadoPrediccion(BaseModel):
    """Resultado de predicción de tiempo."""
    distancia: float
    nivel_trafico: str
    hora: int
    tiempo_predicho: float
    confianza: str  # Alta, Media, Baja
    modelo_usado: str
    metricas: Optional[Dict[str, float]] = None


# ==================== Análisis ====================
class EstadisticasTiempo(BaseModel):
    promedio: float
    mediana: float
    minimo: float
    maximo: float
    desviacion_std: float


class AnalisisDatosResponse(BaseModel):
    """Respuesta de análisis de datos."""
    total_registros: int
    ciudades_disponibles: List[str]
    calles_por_ciudad: Dict[str, int]
    estadisticas_trafico: Dict[str, int]
    estadisticas_tiempo: EstadisticasTiempo
    registros_recientes: Optional[List[Dict[str, Any]]] = None


# ==================== Health ====================
class HealthResponse(BaseModel):
    """Estado de salud del sistema."""
    estado: str
    componentes: Dict[str, bool]
    version: str = "2.0.0"
    timestamp: datetime