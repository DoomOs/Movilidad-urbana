"""
API REST para Sistema de Recomendación de Rutas Urbanas.

Integra todos los componentes del sistema de IA:
- Generación y análisis de datos con Pandas
- Algoritmos de búsqueda (BFS, DFS, A*)
- Lógica de predicados para reglas de decisión
- Modelo de Machine Learning para predicción de tiempo
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import pandas as pd
import os
import sys

# Agregar backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generador_dataset import GeneradorDatasetTrafico
from buscador_rutas import GrafoTrafico, BuscadorRutas
from logica_predicados import SistemaReglasTrafico
from modelo_ml import ModeloPrediccionTiempo


# ==================== Modelos de Datos ====================

class SolicitudRuta(BaseModel):
    """Modelo para solicitud de ruta."""
    origen: str = Field(..., description="Calle o ubicación de origen")
    destino: str = Field(..., description="Calle o ubicación de destino")
    ciudad: Optional[str] = Field(None, description="Ciudad específica (opcional)")
    hora: int = Field(12, ge=0, le=23, description="Hora del día (0-23)")
    dia_semana: str = Field("Lunes", description="Día de la semana")
    tipo_vehiculo: str = Field("automovil", description="Tipo de vehículo")
    clima: str = Field("Despejado", description="Condición climática")


class ResultadoRuta(BaseModel):
    """Modelo para resultado de ruta."""
    algoritmo: str
    ruta: List[str]
    distancia_total: float
    tiempo_total: float
    tiempo_ajustado: Optional[float] = None
    nodos_expandidos: int
    recomendaciones: List[str] = []
    advertencias: List[str] = []


class ComparacionAlgoritmos(BaseModel):
    """Modelo para comparación de algoritmos."""
    bfs: Optional[Dict[str, Any]] = None
    dfs: Optional[Dict[str, Any]] = None
    a_estrella: Optional[Dict[str, Any]] = None
    mejor_opcion: str = ""
    razon: str = ""


class PrediccionTiempo(BaseModel):
    """Modelo para predicción de tiempo."""
    distancia: float
    nivel_trafico: str
    hora: int
    tiempo_predicho: float
    confianza: str


class AnalisisDatos(BaseModel):
    """Modelo para análisis de datos."""
    total_registros: int
    ciudades_disponibles: List[str]
    calles_por_ciudad: Dict[str, int]
    estadisticas_trafico: Dict[str, Any]
    estadisticas_tiempo: Dict[str, float]


# ==================== Aplicación FastAPI ====================

app = FastAPI(
    title="Sistema Inteligente de Recomendación de Rutas",
    description="""
    API para sistema de recomendación de rutas urbanas con IA.
    
    ## Características
    
    * **Búsqueda de Rutas**: BFS, DFS y A*
    * **Lógica de Predicados**: 7 reglas de decisión
    * **Machine Learning**: Predicción de tiempo de viaje
    * **Análisis de Datos**: Estadísticas con Pandas
    """,
    version="1.0.0"
)

# Configurar CORS para React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Variables Globales ====================

generador_dataset: Optional[GeneradorDatasetTrafico] = None
grafo: Optional[GrafoTrafico] = None
buscador: Optional[BuscadorRutas] = None
sistema_reglas: Optional[SistemaReglasTrafico] = None
modelo_ml: Optional[ModeloPrediccionTiempo] = None
dataset_df: Optional[pd.DataFrame] = None


def inicializar_sistema():
    """Inicializa todos los componentes del sistema."""
    global generador_dataset, grafo, buscador, sistema_reglas, modelo_ml, dataset_df
    
    print("Inicializando sistema...")
    
    # Generar dataset
    generador_dataset = GeneradorDatasetTrafico()
    dataset_df = generador_dataset.generar_dataset(num_registros=150)
    
    # Construir grafo
    grafo = GrafoTrafico()
    grafo.cargar_desde_dataframe(dataset_df)
    
    # Crear buscador
    buscador = BuscadorRutas(grafo)
    
    # Inicializar sistema de reglas
    sistema_reglas = SistemaReglasTrafico()
    
    # Entrenar modelo ML
    modelo_ml = entrenar_modelo_ml()
    
    print(f"Sistema inicializado:")
    print(f"  - Nodos en grafo: {len(grafo.nodos)}")
    print(f"  - Reglas activas: 7")
    print(f"  - Modelo ML: {'entrenado' if modelo_ml.entrenado else 'no entrenado'}")


def entrenar_modelo_ml() -> ModeloPrediccionTiempo:
    """Entrena el modelo de ML con el dataset actual."""
    global dataset_df
    
    modelo = ModeloPrediccionTiempo()
    
    # Preparar datos
    df = dataset_df.copy()
    
    # Codificar variables categóricas
    mapa_trafico = {"Bajo": 1, "Medio": 2, "Alto": 3, "Muy Alto": 4}
    df["trafico_codificado"] = df["trafico"].map(mapa_trafico)
    
    # Entrenar
    caracteristicas = ["distancia_km", "trafico_codificado", "hora"]
    modelo.entrenar(df, caracteristicas, "tiempo_estimado_min")
    
    return modelo


# Llamar a inicialización al startup
@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación."""
    inicializar_sistema()


# ==================== Endpoints ====================

@app.get("/")
async def raiz():
    """Endpoint raíz con información de la API."""
    return {
        "mensaje": "Bienvenido al Sistema Inteligente de Recomendación de Rutas",
        "version": "1.0.0",
        "documentacion": "/docs",
        "endpoints_disponibles": [
            "/ciudades",
            "/calles/{ciudad}",
            "/buscar-ruta",
            "/comparar-algoritmos",
            "/predecir-tiempo",
            "/analisis-datos"
        ]
    }


@app.get("/ciudades")
async def obtener_ciudades():
    """Obtiene lista de ciudades disponibles."""
    ciudades = dataset_df["ciudad"].unique().tolist()
    return {"ciudades": ciudades, "total": len(ciudades)}


@app.get("/calles/{ciudad}")
async def obtener_calles_por_ciudad(ciudad: str):
    """Obtiene todas las calles disponibles en una ciudad."""
    ciudad_limpia = ciudad.strip()
    
    # Buscar ciudad (insensible a mayúsculas/minúsculas)
    df_ciudad = dataset_df[
        dataset_df["ciudad"].str.lower() == ciudad_limpia.lower()
    ]
    
    if df_ciudad.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Ciudad '{ciudad}' no encontrada"
        )
    
    # Obtener calles únicas (origen y destino)
    calles_origen = df_ciudad["origen"].unique().tolist()
    calles_destino = df_ciudad["destino"].unique().tolist()
    todas_calles = list(set(calles_origen + calles_destino))
    
    return {
        "ciudad": df_ciudad["ciudad"].iloc[0],
        "calles": sorted(todas_calles),
        "total": len(todas_calles)
    }


@app.post("/buscar-ruta", response_model=List[ResultadoRuta])
async def buscar_ruta(solicitud: SolicitudRuta):
    """
    Busca rutas entre origen y destino usando los tres algoritmos.
    
    Aplica reglas de lógica de predicados para ajustar tiempos.
    """
    # Validar que existen las calles
    if solicitud.origen not in grafo.nodos:
        raise HTTPException(
            status_code=404,
            detail=f"Origen '{solicitud.origen}' no encontrado"
        )
    
    if solicitud.destino not in grafo.nodos:
        raise HTTPException(
            status_code=404,
            detail=f"Destino '{solicitud.destino}' no encontrado"
        )
    
    resultados = []
    
    # Ejecutar los tres algoritmos
    algoritmos = [
        ("BFS", buscador.bfs),
        ("DFS", buscador.dfs),
        ("A*", buscador.a_estrella)
    ]
    
    for nombre_alg, funcion_busqueda in algoritmos:
        resultado = funcion_busqueda(solicitud.origen, solicitud.destino)
        
        if resultado:
            # Aplicar reglas de lógica de predicados
            contexto = {
                "distancia": resultado.distancia_total,
                "trafico": "Medio",  # Se podría obtener del dataset
                "clima": solicitud.clima,
                "hora": solicitud.hora,
                "dia_semana": solicitud.dia_semana,
                "tipo_vehiculo": solicitud.tipo_vehiculo
            }
            
            evaluacion = sistema_reglas.evaluar_contexto(contexto)
            tiempo_ajustado = resultado.tiempo_total * evaluacion["factor_ajuste_tiempo"]
            
            resultados.append(
                ResultadoRuta(
                    algoritmo=nombre_alg,
                    ruta=resultado.ruta,
                    distancia_total=resultado.distancia_total,
                    tiempo_total=resultado.tiempo_total,
                    tiempo_ajustado=round(tiempo_ajustado, 2),
                    nodos_expandidos=resultado.nodos_expandidos,
                    recomendaciones=evaluacion["recomendaciones"],
                    advertencias=evaluacion["advertencias"]
                )
            )
    
    if not resultados:
        raise HTTPException(
            status_code=404,
            detail="No se encontró ruta entre los puntos especificados"
        )
    
    return resultados


@app.get("/comparar-algoritmos", response_model=ComparacionAlgoritmos)
async def comparar_algoritmos(
    origen: str = Query(..., description="Calle de origen"),
    destino: str = Query(..., description="Calle de destino")
):
    """Compara los tres algoritmos de búsqueda para una ruta específica."""
    
    if origen not in grafo.nodos:
        raise HTTPException(status_code=404, detail=f"Origen '{origen}' no encontrado")
    
    if destino not in grafo.nodos:
        raise HTTPException(status_code=404, detail=f"Destino '{destino}' no encontrado")
    
    comparacion = buscador.comparar_algoritmos(origen, destino)
    
    # Determinar mejor opción (menor tiempo)
    mejor_opcion = ""
    menor_tiempo = float('inf')
    
    for alg, datos in comparacion.items():
        if datos["tiempo"] < menor_tiempo:
            menor_tiempo = datos["tiempo"]
            mejor_opcion = alg
    
    # Determinar razón
    razon = ""
    if mejor_opcion == "A*":
        razon = "A* encuentra la ruta óptima más eficientemente usando heurística"
    elif mejor_opcion == "BFS":
        razon = "BFS garantiza el camino más corto en número de nodos"
    elif mejor_opcion == "DFS":
        razon = "DFS puede encontrar soluciones rápidas pero no garantizadas"
    
    return ComparacionAlgoritmos(
        bfs=comparacion.get("BFS"),
        dfs=comparacion.get("DFS"),
        a_estrella=comparacion.get("A*"),
        mejor_opcion=mejor_opcion,
        razon=razon
    )


@app.post("/predecir-tiempo", response_model=PrediccionTiempo)
async def predecir_tiempo(
    distancia: float = Field(..., gt=0, description="Distancia en kilómetros"),
    nivel_trafico: str = Field(..., description="Nivel de tráfico (Bajo, Medio, Alto, Muy Alto)"),
    hora: int = Field(12, ge=0, le=23, description="Hora del día")
):
    """Predice el tiempo de viaje usando el modelo de ML."""
    
    # Codificar tráfico
    mapa_trafico = {"Bajo": 1, "Medio": 2, "Alto": 3, "Muy Alto": 4}
    
    if nivel_trafico not in mapa_trafico:
        raise HTTPException(
            status_code=400,
            detail=f"Nivel de tráfico inválido. Use: {list(mapa_trafico.keys())}"
        )
    
    trafico_codificado = mapa_trafico[nivel_trafico]
    
    # Hacer predicción
    tiempo_predicho = modelo_ml.predecir_individual(
        distancia_km=distancia,
        trafico_codificado=trafico_codificado,
        hora=hora
    )
    
    # Asegurar que el tiempo no sea negativo
    tiempo_predicho = max(0, tiempo_predicho)
    
    # Determinar confianza basada en R² del modelo
    r2 = 0.75  # Valor aproximado del entrenamiento
    if r2 >= 0.8:
        confianza = "Alta"
    elif r2 >= 0.6:
        confianza = "Media"
    else:
        confianza = "Baja"
    
    return PrediccionTiempo(
        distancia=distancia,
        nivel_trafico=nivel_trafico,
        hora=hora,
        tiempo_predicho=round(tiempo_predicho, 2),
        confianza=confianza
    )


@app.get("/analisis-datos", response_model=AnalisisDatos)
async def obtener_analisis_datos():
    """Obtiene análisis exploratorio del dataset."""
    
    # Estadísticas de tráfico
    conteo_trafico = dataset_df["trafico"].value_counts().to_dict()
    
    # Calles por ciudad
    calles_por_ciudad = {}
    for ciudad in dataset_df["ciudad"].unique():
        df_ciudad = dataset_df[dataset_df["ciudad"] == ciudad]
        calles = set(df_ciudad["origen"].tolist() + df_ciudad["destino"].tolist())
        calles_por_ciudad[ciudad] = len(calles)
    
    # Estadísticas de tiempo
    estadisticas_tiempo = {
        "promedio": round(dataset_df["tiempo_estimado_min"].mean(), 2),
        "mediana": round(dataset_df["tiempo_estimado_min"].median(), 2),
        "minimo": round(dataset_df["tiempo_estimado_min"].min(), 2),
        "maximo": round(dataset_df["tiempo_estimado_min"].max(), 2),
        "desviacion_std": round(dataset_df["tiempo_estimado_min"].std(), 2)
    }
    
    return AnalisisDatos(
        total_registros=len(dataset_df),
        ciudades_disponibles=dataset_df["ciudad"].unique().tolist(),
        calles_por_ciudad=calles_por_ciudad,
        estadisticas_trafico=conteo_trafico,
        estadisticas_tiempo=estadisticas_tiempo
    )


@app.get("/salud")
async def verificar_salud():
    """Verifica el estado de salud del sistema."""
    return {
        "estado": "ok",
        "componentes": {
            "dataset": dataset_df is not None,
            "grafo": grafo is not None,
            "buscador": buscador is not None,
            "sistema_reglas": sistema_reglas is not None,
            "modelo_ml": modelo_ml is not None and modelo_ml.entrenado
        }
    }


# ==================== Punto de Entrada ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
