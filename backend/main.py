"""
API Principal - Sistema Inteligente de Movilidad Urbana Guatemala
FastAPI + SQLAlchemy + ML
"""
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import time

from database import engine, get_db, Base, SessionLocal
from models import Ciudad, Calle, RegistroTrafico, Nodo, Arista, BusquedaHistorial
from schemas import (
    SolicitudRuta, ResultadoRuta, ComparacionAlgoritmos,
    ResultadoPrediccion, AnalisisDatosResponse,
    CiudadResponse, CalleResponse, HealthResponse
)
from seeds import seed_database
from busqueda import crear_grafo_desde_db, BuscadorRutas
from rules import MotorReglas, evaluar_ruta
from ml_modelo import ModeloPredictor, entrenar_y_guardar


# ==================== App Setup ====================
app = FastAPI(
    title="Sistema Inteligente de Movilidad Urbana - Guatemala",
    description="""
    🚗 Sistema de recomendación de rutas urbanas con IA para Guatemala.

    ## Características
    - **Búsqueda de Rutas**: BFS, DFS y A* para encontrar rutas óptimas
    - **Lógica de Predicados**: 8 reglas de decisión para ajustar recomendaciones
    - **Machine Learning**: Regresión Lineal, Random Forest y Gradient Boosting
    - **Datos de Guatemala**: 10 ciudades con calles reales

    ## Ciudades Disponibles
    - Ciudad de Guatemala, Antigua, Quetzaltenango, Escuintla
    - Puerto San José, Cobán, Zacapa, Chiquimula, Retalhuleu, Mazatenango
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Lifecycle ====================
ml_modelo: Optional[ModeloPredictor] = None
motor_reglas = MotorReglas()
grafo_cache: Optional[dict] = None
grafo_timestamp: float = 0


@app.on_event("startup")
async def startup_event():
    """Inicializar sistema al arrancar."""
    global grafo_cache, grafo_timestamp, ml_modelo

    print("\n" + "="*60)
    print("  Sistema de Movilidad Urbana - Guatemala")
    print("="*60 + "\n")

    # Crear tablas
    Base.metadata.create_all(bind=engine)
    print("[OK] Base de datos inicializada")

    # Seed datos si necesario
    try:
        seed_database()
        print("[OK] Datos de Guatemala cargados")
    except Exception as e:
        print(f"  Seed: {e}")

    # Entrenar/cargar modelo ML
    try:
        ml_modelo = entrenar_y_guardar()
        print("[OK] Modelos ML listos")
    except Exception as e:
        print(f"  ML: {e}")

    # Construir grafo inicial
    grafo_cache = construir_grafo()
    grafo_timestamp = time.time()
    print(f"[OK] Grafo construido: {len(grafo_cache.nodos)} nodos")

    print("\n" + "="*60)
    print("  Sistema listo [OK]")
    print("="*60 + "\n")


def construir_grafo():
    """Construir grafo de búsqueda desde la BD."""
    db = SessionLocal()
    try:
        return crear_grafo_desde_db(db)
    finally:
        db.close()


# ==================== Health ====================
@app.get("/salud", response_model=HealthResponse, tags=["Sistema"])
async def health_check():
    """Verificar estado del sistema."""
    return HealthResponse(
        estado="operativo",
        componentes={
            "base_datos": True,
            "motor_reglas": True,
            "modelo_ml": ml_modelo is not None and ml_modelo.entrenado,
            "grafo": grafo_cache is not None
        },
        timestamp=datetime.now()
    )


@app.get("/", tags=["Sistema"])
async def root():
    """Endpoint raíz con información del API."""
    return {
        "mensaje": "Sistema Inteligente de Movilidad Urbana - Guatemala",
        "version": "2.0.0",
        "documentacion": "/docs",
        "ciudades": 10,
        "endpoints": [
            "GET /ciudades - Lista de ciudades",
            "GET /calles/{ciudad} - Calles de una ciudad",
            "POST /buscar-ruta - Buscar ruta con 3 algoritmos",
            "GET /comparar-algoritmos - Comparar BFS/DFS/A*",
            "POST /predecir-tiempo - Predicción ML",
            "GET /analisis-datos - Estadísticas del dataset",
            "GET /metricas-ml - Métricas de modelos"
        ]
    }


# ==================== Datos ====================
@app.get("/ciudades", response_model=list[CiudadResponse], tags=["Datos"])
async def get_ciudades(db: Session = Depends(get_db)):
    """Obtener todas las ciudades disponibles."""
    ciudades = db.query(Ciudad).all()
    result = []
    for c in ciudades:
        num_calles = db.query(Calle).filter(Calle.ciudad_id == c.id).count()
        result.append(CiudadResponse(
            id=c.id,
            nombre=c.nombre,
            departamento=c.departamento,
            latitud=c.latitud,
            longitud=c.longitud,
            num_calles=num_calles
        ))
    return result


@app.get("/calles/{ciudad}", tags=["Datos"])
async def get_calles_ciudad(ciudad: str, db: Session = Depends(get_db)):
    """Obtener todas las calles de una ciudad."""
    ciudad_bd = db.query(Ciudad).filter(
        Ciudad.nombre.ilike(f"%{ciudad}%")
    ).first()

    if not ciudad_bd:
        raise HTTPException(status_code=404, detail=f"Ciudad '{ciudad}' no encontrada")

    calles = db.query(Calle).filter(Calle.ciudad_id == ciudad_bd.id).all()

    return {
        "ciudad": ciudad_bd.nombre,
        "departamento": ciudad_bd.departamento,
        "latitud": ciudad_bd.latitud,
        "longitud": ciudad_bd.longitud,
        "calles": [c.nombre for c in calles],
        "total": len(calles)
    }


# ==================== Búsqueda de Rutas ====================
@app.post("/buscar-ruta", response_model=list[ResultadoRuta], tags=["Rutas"])
async def buscar_ruta(solicitud: SolicitudRuta, db: Session = Depends(get_db)):
    """Buscar ruta entre origen y destino usando los tres algoritmos."""
    global grafo_cache, grafo_timestamp

    # Reconstruir grafo si tiene más de 5 minutos
    if time.time() - grafo_timestamp > 300 or grafo_cache is None:
        grafo_cache = construir_grafo()
        grafo_timestamp = time.time()

    grafo = grafo_cache

    # Verificar que existen origen y destino
    if solicitud.origen not in grafo.nodos:
        raise HTTPException(status_code=404, detail=f"Origen '{solicitud.origen}' no encontrado")
    if solicitud.destino not in grafo.nodos:
        raise HTTPException(status_code=404, detail=f"Destino '{solicitud.destino}' no encontrado")

    # Crear buscador
    buscador = BuscadorRutas(grafo)

    # Ejecutar los tres algoritmos
    resultados_bfs = buscador.bfs(solicitud.origen, solicitud.destino)
    resultados_dfs = buscador.dfs(solicitud.origen, solicitud.destino)
    resultados_a = buscador.a_estrella(solicitud.origen, solicitud.destino)

    # Contexto para reglas
    contexto = {
        "trafico": "Medio",
        "distancia": 0,
        "clima": solicitud.clima.value if hasattr(solicitud.clima, 'value') else solicitud.clima,
        "hora": solicitud.hora,
        "dia": solicitud.dia_semana.value if hasattr(solicitud.dia_semana, 'value') else solicitud.dia_semana.value,
        "vehiculo": solicitud.tipo_vehiculo.value if hasattr(solicitud.tipo_vehiculo, 'value') else solicitud.tipo_vehiculo,
        "combustible": "normal"
    }

    respuestas = []

    for result in [resultados_bfs, resultados_dfs, resultados_a]:
        if result:
            contexto["distancia"] = result.distancia_total

            evaluacion = motor_reglas.evaluar(contexto)
            tiempo_ajustado = result.tiempo_total * evaluacion["factor_tiempo"]

            respuestas.append(ResultadoRuta(
                algoritmo=result.algoritmo,
                ruta=result.ruta,
                distancia_total=result.distancia_total,
                tiempo_total=result.tiempo_total,
                tiempo_ajustado=round(tiempo_ajustado, 2),
                nodos_expandidos=result.nodos_expandidos,
                recomendaciones=evaluacion["recomendaciones"],
                advertencias=evaluacion["advertencias"],
                coordenadas_ruta=result.coordenadas_ruta
            ))

    if not respuestas:
        raise HTTPException(status_code=404, detail="No se encontró ruta entre los puntos")

    # Guardar en historial
    try:
        historial = BusquedaHistorial(
            ciudad=solicitud.ciudad or "Unknown",
            origen=solicitud.origen,
            destino=solicitud.destino,
            hora=solicitud.hora,
            dia_semana=solicitud.dia_semana.value if hasattr(solicitud.dia_semana, 'value') else str(solicitud.dia_semana),
            vehiculo=solicitud.tipo_vehiculo.value if hasattr(solicitud.tipo_vehiculo, 'value') else str(solicitud.tipo_vehiculo),
            clima=solicitud.clima.value if hasattr(solicitud.clima, 'value') else str(solicitud.clima),
            resultado_json=str(respuestas),
            mejor_algoritmo=min(respuestas, key=lambda x: x.tiempo_total).algoritmo if respuestas else None
        )
        db.add(historial)
        db.commit()
    except Exception:
        pass

    return respuestas


@app.get("/comparar-algoritmos", response_model=ComparacionAlgoritmos, tags=["Rutas"])
async def comparar_algoritmos(
    origen: str = Query(..., description="Calle de origen"),
    destino: str = Query(..., description="Calle de destino"),
    db: Session = Depends(get_db)
):
    """Comparar los tres algoritmos de búsqueda."""
    global grafo_cache

    if grafo_cache is None:
        grafo_cache = construir_grafo()

    grafo = grafo_cache

    if origen not in grafo.nodos:
        raise HTTPException(status_code=404, detail=f"Origen '{origen}' no encontrado")
    if destino not in grafo.nodos:
        raise HTTPException(status_code=404, detail=f"Destino '{destino}' no encontrado")

    buscador = BuscadorRutas(grafo)

    resultados = buscador.comparar_todos(origen, destino)

    comparacion = ComparacionAlgoritmos()

    if "BFS" in resultados:
        r = resultados["BFS"]
        comparacion.bfs = {
            "ruta": r.ruta,
            "distancia": r.distancia_total,
            "tiempo": r.tiempo_total,
            "nodos_expandidos": r.nodos_expandidos,
            "tiempo_busqueda_ms": r.tiempo_busqueda_ms
        }

    if "DFS" in resultados:
        r = resultados["DFS"]
        comparacion.dfs = {
            "ruta": r.ruta,
            "distancia": r.distancia_total,
            "tiempo": r.tiempo_total,
            "nodos_expandidos": r.nodos_expandidos,
            "tiempo_busqueda_ms": r.tiempo_busqueda_ms
        }

    if "A*" in resultados:
        r = resultados["A*"]
        comparacion.a_estrella = {
            "ruta": r.ruta,
            "distancia": r.distancia_total,
            "tiempo": r.tiempo_total,
            "nodos_expandidos": r.nodos_expandidos,
            "tiempo_busqueda_ms": r.tiempo_busqueda_ms
        }

    # Determinar mejor opción (menor tiempo)
    mejor = None
    menor_tiempo = float('inf')
    for nombre, datos in [("BFS", comparacion.bfs), ("DFS", comparacion.dfs), ("A*", comparacion.a_estrella)]:
        if datos and datos["tiempo"] < menor_tiempo:
            menor_tiempo = datos["tiempo"]
            mejor = nombre

    if mejor:
        comparacion.mejor_opcion = mejor
        comparacion.razon = {
            "A*": "A* encuentra la ruta óptima más eficientemente usando heurística euclidiana",
            "BFS": "BFS garantiza el camino más corto en número de nodos expandidos",
            "DFS": "DFS puede encontrar soluciones rápidas en grafos densos"
        }.get(mejor, "")

    return comparacion


# ==================== ML Predicción ====================
@app.post("/predecir-tiempo", response_model=ResultadoPrediccion, tags=["ML"])
async def predecir_tiempo(
    distancia: float = Query(..., gt=0, description="Distancia en km"),
    nivel_trafico: str = Query(..., description="Nivel de tráfico"),
    hora: int = Query(..., ge=0, le=23, description="Hora del día")
):
    """Predecir tiempo de viaje usando modelos ML."""
    global ml_modelo

    if ml_modelo is None or not ml_modelo.entrenado:
        raise HTTPException(status_code=503, detail="Modelo ML no disponible. Intente más tarde.")

    if nivel_trafico not in ["Bajo", "Medio", "Alto", "Muy Alto"]:
        raise HTTPException(status_code=400, detail=f"Nivel de tráfico inválido: {nivel_trafico}")

    resultado = ml_modelo.predecir(distancia, nivel_trafico, hora)

    return ResultadoPrediccion(
        distancia=resultado["distancia"],
        nivel_trafico=resultado["nivel_trafico"],
        hora=resultado["hora"],
        tiempo_predicho=resultado["tiempo_predicho"],
        confianza=resultado["confianza"],
        modelo_usado=resultado["modelo_usado"],
        metricas={"r2": resultado["r2_score"], "mae": resultado["mae"]}
    )


@app.get("/metricas-ml", tags=["ML"])
async def get_metricas_ml():
    """Obtener métricas de todos los modelos ML."""
    global ml_modelo

    if ml_modelo is None or not ml_modelo.entrenado:
        return {"error": "Modelos no entrenados"}

    metricas = ml_modelo.obtener_metricas_modelos()

    return {
        "modelos": metricas,
        "mejor_por_r2": max(metricas.items(), key=lambda x: x[1]["r2"])[0] if metricas else None,
        "mejor_por_mae": min(metricas.items(), key=lambda x: x[1]["mae"])[0] if metricas else None
    }


@app.get("/comparar-modelos", tags=["ML"])
async def comparar_modelos(
    distancia: float = Query(5.0, gt=0),
    nivel_trafico: str = Query("Medio"),
    hora: int = Query(12, ge=0, le=23)
):
    """Comparar predicciones de todos los modelos."""
    global ml_modelo

    if ml_modelo is None or not ml_modelo.entrenado:
        raise HTTPException(status_code=503, detail="Modelo ML no disponible")

    resultados = ml_modelo.obtener_comparacion(distancia, nivel_trafico, hora)

    return {
        "entrada": {"distancia_km": distancia, "nivel_trafico": nivel_trafico, "hora": hora},
        "predicciones": resultados
    }


# ==================== Análisis ====================
@app.get("/analisis-datos", response_model=AnalisisDatosResponse, tags=["Análisis"])
async def analisis_datos(db: Session = Depends(get_db)):
    """Obtener análisis exploratorio completo del dataset."""
    registros = db.query(RegistroTrafico).all()

    if not registros:
        return AnalisisDatosResponse(
            total_registros=0,
            ciudades_disponibles=[],
            calles_por_ciudad={},
            estadisticas_trafico={},
            estadisticas_tiempo={"promedio": 0, "mediana": 0, "minimo": 0, "maximo": 0, "desviacion_std": 0}
        )

    # Estadísticas de tráfico
    conteo_trafico = {}
    for r in registros:
        trafico_val = r.trafico.value if hasattr(r.trafico, 'value') else r.trafico
        conteo_trafico[trafico_val] = conteo_trafico.get(trafico_val, 0) + 1

    # Calles por ciudad
    calles_por_ciudad = {}
    ciudades = db.query(Ciudad).all()
    for c in ciudades:
        num = db.query(Calle).filter(Calle.ciudad_id == c.id).count()
        calles_por_ciudad[c.nombre] = num

    # Estadísticas de tiempo
    tiempos = [r.tiempo_estimado_min for r in registros]
    import statistics
    promedio = round(statistics.mean(tiempos), 2)
    mediana = round(statistics.median(tiempos), 2)
    minimo = round(min(tiempos), 2)
    maximo = round(max(tiempos), 2)
    desviacion = round(statistics.stdev(tiempos), 2) if len(tiempos) > 1 else 0

    # Últimos registros
    registros_recientes = []
    for r in registros[:10]:
        registros_recientes.append({
            "id": r.id,
            "origen": db.query(Calle).filter(Calle.id == r.origen_id).first().nombre if r.origen_id else "N/A",
            "destino": db.query(Calle).filter(Calle.id == r.destino_id).first().nombre if r.destino_id else "N/A",
            "distancia_km": r.distancia_km,
            "tiempo_min": r.tiempo_estimado_min,
            "trafico": r.trafico.value if hasattr(r.trafico, 'value') else r.trafico
        })

    return AnalisisDatosResponse(
        total_registros=len(registros),
        ciudades_disponibles=[c.nombre for c in ciudades],
        calles_por_ciudad=calles_por_ciudad,
        estadisticas_trafico=conteo_trafico,
        estadisticas_tiempo={
            "promedio": promedio,
            "mediana": mediana,
            "minimo": minimo,
            "maximo": maximo,
            "desviacion_std": desviacion
        },
        registros_recientes=registros_recientes
    )


@app.get("/historial", tags=["Análisis"])
async def get_historial(db: Session = Depends(get_db)):
    """Obtener historial de búsquedas."""
    historial = db.query(BusquedaHistorial).order_by(
        BusquedaHistorial.created_at.desc()
    ).limit(50).all()

    return {
        "total": len(historial),
        "busquedas": [
            {
                "ciudad": h.ciudad,
                "origen": h.origen,
                "destino": h.destino,
                "hora": h.hora,
                "dia_semana": h.dia_semana,
                "mejor_algoritmo": h.mejor_algoritmo,
                "created_at": h.created_at.isoformat() if h.created_at else None
            }
            for h in historial
        ]
    }


# ==================== Debug ====================
@app.get("/debug-grafo", tags=["Debug"])
async def debug_grafo():
    """Debug: información del grafo en caché."""
    global grafo_cache, grafo_timestamp

    if grafo_cache is None:
        return {"error": "Grafo no construido"}

    return {
        "nodos_count": len(grafo_cache.nodos),
        "aristas_count": sum(len(v) for v in grafo_cache.aristas.values()),
        "nodos_sample": list(grafo_cache.nodos.keys())[:10],
        "timestamp": grafo_timestamp
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)