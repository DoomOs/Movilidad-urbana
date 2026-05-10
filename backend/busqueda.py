"""
Algoritmos de búsqueda para encontrar rutas óptimas.
BFS, DFS y A* para búsqueda de rutas en el grafo de tráfico.
"""
from collections import deque
from typing import List, Dict, Tuple, Optional, Set
import heapq
from dataclasses import dataclass
import math


@dataclass
class ResultadoBusqueda:
    """Resultado de una búsqueda de ruta."""
    algoritmo: str
    ruta: List[str]
    distancia_total: float
    tiempo_total: float
    nodos_expandidos: int
    tiempo_busqueda_ms: float
    coordenadas_ruta: Optional[List[Dict[str, float]]] = None


class GrafoBusqueda:
    """Grafo en memoria para búsqueda de rutas."""

    def __init__(self):
        self.nodos: Dict[str, Dict] = {}
        self.aristas: Dict[str, List[Dict]] = {}

    def agregar_nodo(self, nombre: str, lat: float = 0, lng: float = 0):
        self.nodos[nombre] = {"lat": lat, "lng": lng}
        if nombre not in self.aristas:
            self.aristas[nombre] = []

    def agregar_arista(self, origen: str, destino: str, distancia: float, tiempo: float, trafico: str = "Medio"):
        if origen not in self.aristas:
            self.aristas[origen] = []
        self.aristas[origen].append({
            "destino": destino,
            "distancia": distancia,
            "tiempo": tiempo,
            "trafico": trafico
        })

    def obtener_vecinos(self, nodo: str) -> List[Dict]:
        return self.aristas.get(nodo, [])

    def _heuristica_euclidiana(self, nodo_actual: str, nodo_destino: str) -> float:
        """Calcula distancia euclidiana entre nodos."""
        if nodo_actual not in self.nodos or nodo_destino not in self.nodos:
            return float('inf')

        c1 = self.nodos[nodo_actual]
        c2 = self.nodos[nodo_destino]

        return math.sqrt((c1["lat"] - c2["lat"])**2 + (c1["lng"] - c2["lng"])**2)


class BuscadorRutas:
    """Implementación de algoritmos BFS, DFS y A*."""

    def __init__(self, grafo: GrafoBusqueda):
        self.grafo = grafo

    def bfs(self, origen: str, destino: str) -> Optional[ResultadoBusqueda]:
        """Breadth-First Search - Búsqueda no informada."""
        import time
        start = time.time()

        if origen not in self.grafo.nodos or destino not in self.grafo.nodos:
            return None

        cola = deque([(origen, [origen], 0.0, 0.0)])
        visitados: Set[str] = set()
        nodos_expandidos = 0

        while cola:
            nodo_actual, ruta, distancia, tiempo = cola.popleft()
            nodos_expandidos += 1

            if nodo_actual == destino:
                elapsed = (time.time() - start) * 1000
                coords = []
                for n in ruta:
                    if n in self.grafo.nodos:
                        coords.append({"lat": self.grafo.nodos[n]["lat"], "lng": self.grafo.nodos[n]["lng"]})

                return ResultadoBusqueda(
                    algoritmo="BFS",
                    ruta=ruta,
                    distancia_total=round(distancia, 2),
                    tiempo_total=round(tiempo, 2),
                    nodos_expandidos=nodos_expandidos,
                    tiempo_busqueda_ms=round(elapsed, 2),
                    coordenadas_ruta=coords
                )

            if nodo_actual in visitados:
                continue
            visitados.add(nodo_actual)

            for arista in self.grafo.obtener_vecinos(nodo_actual):
                if arista["destino"] not in visitados:
                    nueva_ruta = ruta + [arista["destino"]]
                    cola.append((
                        arista["destino"],
                        nueva_ruta,
                        distancia + arista["distancia"],
                        tiempo + arista["tiempo"]
                    ))

        return None

    def dfs(self, origen: str, destino: str) -> Optional[ResultadoBusqueda]:
        """Depth-First Search - Búsqueda no informada."""
        import time
        start = time.time()

        if origen not in self.grafo.nodos or destino not in self.grafo.nodos:
            return None

        pila = [(origen, [origen], 0.0, 0.0)]
        visitados: Set[str] = set()
        nodos_expandidos = 0

        while pila:
            nodo_actual, ruta, distancia, tiempo = pila.pop()
            nodos_expandidos += 1

            if nodo_actual == destino:
                elapsed = (time.time() - start) * 1000
                coords = []
                for n in ruta:
                    if n in self.grafo.nodos:
                        coords.append({"lat": self.grafo.nodos[n]["lat"], "lng": self.grafo.nodos[n]["lng"]})

                return ResultadoBusqueda(
                    algoritmo="DFS",
                    ruta=ruta,
                    distancia_total=round(distancia, 2),
                    tiempo_total=round(tiempo, 2),
                    nodos_expandidos=nodos_expandidos,
                    tiempo_busqueda_ms=round(elapsed, 2),
                    coordenadas_ruta=coords
                )

            if nodo_actual in visitados:
                continue
            visitados.add(nodo_actual)

            for arista in self.grafo.obtener_vecinos(nodo_actual):
                if arista["destino"] not in visitados:
                    pila.append((
                        arista["destino"],
                        ruta + [arista["destino"]],
                        distancia + arista["distancia"],
                        tiempo + arista["tiempo"]
                    ))

        return None

    def a_estrella(self, origen: str, destino: str) -> Optional[ResultadoBusqueda]:
        """A* Search - Búsqueda informada con heurística euclidiana."""
        import time
        start = time.time()

        if origen not in self.grafo.nodos or destino not in self.grafo.nodos:
            return None

        # Cola de prioridad: (f_score, g_score, nodo, ruta, distancia, tiempo)
        h_inicial = self._heuristica_euclidiana(origen, destino)
        cola = [(h_inicial, 0.0, origen, [origen], 0.0, 0.0)]

        g_score: Dict[str, float] = {origen: 0.0}
        visitados: Set[str] = set()
        nodos_expandidos = 0

        while cola:
            _, _, nodo_actual, ruta, distancia, tiempo = heapq.heappop(cola)
            nodos_expandidos += 1

            if nodo_actual == destino:
                elapsed = (time.time() - start) * 1000
                coords = []
                for n in ruta:
                    if n in self.grafo.nodos:
                        coords.append({"lat": self.grafo.nodos[n]["lat"], "lng": self.grafo.nodos[n]["lng"]})

                return ResultadoBusqueda(
                    algoritmo="A*",
                    ruta=ruta,
                    distancia_total=round(distancia, 2),
                    tiempo_total=round(tiempo, 2),
                    nodos_expandidos=nodos_expandidos,
                    tiempo_busqueda_ms=round(elapsed, 2),
                    coordenadas_ruta=coords
                )

            if nodo_actual in visitados:
                continue
            visitados.add(nodo_actual)

            for arista in self.grafo.obtener_vecinos(nodo_actual):
                if arista["destino"] in visitados:
                    continue

                nuevo_g = g_score[nodo_actual] + arista["tiempo"]

                if arista["destino"] not in g_score or nuevo_g < g_score[arista["destino"]]:
                    g_score[arista["destino"]] = nuevo_g
                    h = self._heuristica_euclidiana(arista["destino"], destino)
                    f = nuevo_g + h

                    heapq.heappush(cola, (
                        f,
                        nuevo_g,
                        arista["destino"],
                        ruta + [arista["destino"]],
                        distancia + arista["distancia"],
                        tiempo + arista["tiempo"]
                    ))

        return None

    def comparar_todos(self, origen: str, destino: str) -> Dict[str, ResultadoBusqueda]:
        """Ejecutar los tres algoritmos y comparar resultados."""
        resultados = {}

        result_bfs = self.bfs(origen, destino)
        if result_bfs:
            resultados["BFS"] = result_bfs

        result_dfs = self.dfs(origen, destino)
        if result_dfs:
            resultados["DFS"] = result_dfs

        result_a = self.a_estrella(origen, destino)
        if result_a:
            resultados["A*"] = result_a

        return resultados


def crear_grafo_desde_db(db) -> GrafoBusqueda:
    """Crear grafo de búsqueda desde la base de datos."""
    from models import Nodo, Arista, Calle

    grafo = GrafoBusqueda()

    # Cargar nodos
    nodos = db.query(Nodo).all()
    for nodo in nodos:
        lat = nodo.latitud or 0
        lng = nodo.longitud or 0
        grafo.agregar_nodo(nodo.nombre, lat, lng)

    # Cargar aristas
    aristas = db.query(Arista).all()
    for arista in aristas:
        origen = db.query(Nodo).filter(Nodo.id == arista.nodo_origen_id).first()
        destino = db.query(Nodo).filter(Nodo.id == arista.nodo_destino_id).first()
        if origen and destino:
            grafo.agregar_arista(
                origen.nombre,
                destino.nombre,
                arista.distancia_km,
                arista.tiempo_min,
                arista.trafico.value if hasattr(arista.trafico, 'value') else arista.trafico
            )

    return grafo