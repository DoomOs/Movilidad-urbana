"""
Motor de Búsqueda para Rutas Urbanas.

Implementación de algoritmos de búsqueda informada y no informada
para encontrar rutas óptimas en entornos urbanos.
"""

import pandas as pd
import numpy as np
from collections import deque
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
import heapq


@dataclass
class Nodo:
    """Representa un nodo en el grafo de búsqueda.
    
    Attributes:
        nombre: Nombre de la calle o ubicación.
        ciudad: Ciudad donde se encuentra el nodo.
        coordenadas: Tupla (x, y) para cálculo de heurísticas.
    """
    nombre: str
    ciudad: str
    coordenadas: Tuple[float, float] = (0.0, 0.0)


@dataclass
class Arista:
    """Representa una conexión entre dos nodos.
    
    Attributes:
        origen: Nodo de origen.
        destino: Nodo de destino.
        distancia: Distancia en kilómetros.
        trafico: Nivel de tráfico.
        tiempo_estimado: Tiempo estimado en minutos.
    """
    origen: str
    destino: str
    distancia: float
    trafico: str
    tiempo_estimado: float


@dataclass
class ResultadoBusqueda:
    """Resultado de una búsqueda de ruta.
    
    Attributes:
        ruta: Lista de nombres de calles en la ruta encontrada.
        distancia_total: Distancia total en kilómetros.
        tiempo_total: Tiempo total estimado en minutos.
        nodos_expandidos: Número de nodos expandidos durante la búsqueda.
        algoritmo: Nombre del algoritmo utilizado.
    """
    ruta: List[str]
    distancia_total: float
    tiempo_total: float
    nodos_expandidos: int
    algoritmo: str


class GrafoTrafico:
    """Grafo que representa la red vial urbana.
    
    Attributes:
        nodos: Diccionario de nodos por nombre.
        aristas: Diccionario de aristas por origen.
        datos: DataFrame con los datos de tráfico.
    """
    
    def __init__(self):
        """Inicializa el grafo vacío."""
        self.nodos: Dict[str, Nodo] = {}
        self.aristas: Dict[str, List[Arista]] = {}
        self.datos: Optional[pd.DataFrame] = None
    
    def cargar_desde_dataframe(self, df: pd.DataFrame) -> None:
        """Carga el grafo desde un DataFrame de pandas.
        
        Args:
            df: DataFrame con columnas origen, destino, distancia_km,
                trafico, tiempo_estimado_min, ciudad.
        """
        self.datos = df.copy()
        
        # Crear nodos únicos
        for _, fila in df.iterrows():
            origen = fila["origen"]
            destino = fila["destino"]
            ciudad = fila["ciudad"]
            
            if origen not in self.nodos:
                # Asignar coordenadas pseudo-aleatorias basadas en el hash del nombre
                coords_origen = self._generar_coordenadas(origen, ciudad)
                self.nodos[origen] = Nodo(nombre=origen, ciudad=ciudad, 
                                         coordenadas=coords_origen)
            
            if destino not in self.nodos:
                coords_destino = self._generar_coordenadas(destino, ciudad)
                self.nodos[destino] = Nodo(nombre=destino, ciudad=ciudad,
                                          coordenadas=coords_destino)
            
            # Crear arista
            arista = Arista(
                origen=origen,
                destino=destino,
                distancia=fila["distancia_km"],
                trafico=fila["trafico"],
                tiempo_estimado=fila["tiempo_estimado_min"]
            )
            
            if origen not in self.aristas:
                self.aristas[origen] = []
            self.aristas[origen].append(arista)
            
            # Añadir arista inversa (grafo no dirigido)
            arista_inversa = Arista(
                origen=destino,
                destino=origen,
                distancia=fila["distancia_km"],
                trafico=fila["trafico"],
                tiempo_estimado=fila["tiempo_estimado_min"]
            )
            
            if destino not in self.aristas:
                self.aristas[destino] = []
            self.aristas[destino].append(arista_inversa)
    
    def _generar_coordenadas(self, nombre: str, ciudad: str) -> Tuple[float, float]:
        """Genera coordenadas pseudo-aleatorias para un nodo.
        
        Args:
            nombre: Nombre del nodo.
            ciudad: Ciudad del nodo.
            
        Returns:
            Tupla (x, y) con coordenadas normalizadas.
        """
        # Usar hash para generar coordenadas consistentes
        hash_nombre = hash(nombre + ciudad)
        x = (hash_nombre % 1000) / 1000.0 * 10  # Rango 0-10
        y = (hash_nombre // 1000 % 1000) / 1000.0 * 10
        return (x, y)
    
    def obtener_vecinos(self, nodo: str) -> List[Arista]:
        """Obtiene las aristas salientes de un nodo.
        
        Args:
            nodo: Nombre del nodo.
            
        Returns:
            Lista de aristas salientes.
        """
        return self.aristas.get(nodo, [])
    
    def calcular_heuristica(self, nodo_actual: str, nodo_destino: str) -> float:
        """Calcula la heurística de distancia euclidiana.
        
        Args:
            nodo_actual: Nombre del nodo actual.
            nodo_destino: Nombre del nodo destino.
            
        Returns:
            Distancia euclidiana estimada.
        """
        if nodo_actual not in self.nodos or nodo_destino not in self.nodos:
            return float('inf')
        
        coords_actual = self.nodos[nodo_actual].coordenadas
        coords_destino = self.nodos[nodo_destino].coordenadas
        
        distancia = np.sqrt(
            (coords_actual[0] - coords_destino[0]) ** 2 +
            (coords_actual[1] - coords_destino[1]) ** 2
        )
        
        return distancia


class BuscadorRutas:
    """Clase principal para búsqueda de rutas usando diferentes algoritmos.
    
    Attributes:
        grafo: Grafo de tráfico urbano.
    """
    
    def __init__(self, grafo: GrafoTrafico):
        """Inicializa el buscador con un grafo.
        
        Args:
            grafo: GrafoTrafico cargado con datos.
        """
        self.grafo = grafo
    
    def bfs(self, origen: str, destino: str) -> Optional[ResultadoBusqueda]:
        """Búsqueda en anchura (BFS) - Búsqueda no informada.
        
        Args:
            origen: Nombre del nodo de origen.
            destino: Nombre del nodo de destino.
            
        Returns:
            ResultadoBusqueda con la ruta encontrada o None si no existe.
        """
        if origen not in self.grafo.nodos or destino not in self.grafo.nodos:
            return None
        
        cola = deque([(origen, [origen], 0.0, 0.0)])
        visitados: Set[str] = set()
        nodos_expandidos = 0
        
        while cola:
            nodo_actual, ruta, distancia, tiempo = cola.popleft()
            nodos_expandidos += 1
            
            if nodo_actual == destino:
                return ResultadoBusqueda(
                    ruta=ruta,
                    distancia_total=round(distancia, 2),
                    tiempo_total=round(tiempo, 2),
                    nodos_expandidos=nodos_expandidos,
                    algoritmo="BFS"
                )
            
            if nodo_actual in visitados:
                continue
            
            visitados.add(nodo_actual)
            
            for arista in self.grafo.obtener_vecinos(nodo_actual):
                if arista.destino not in visitados:
                    nueva_ruta = ruta + [arista.destino]
                    nueva_distancia = distancia + arista.distancia
                    nuevo_tiempo = tiempo + arista.tiempo_estimado
                    cola.append((arista.destino, nueva_ruta, 
                               nueva_distancia, nuevo_tiempo))
        
        return None
    
    def dfs(self, origen: str, destino: str) -> Optional[ResultadoBusqueda]:
        """Búsqueda en profundidad (DFS) - Búsqueda no informada.
        
        Args:
            origen: Nombre del nodo de origen.
            destino: Nombre del nodo de destino.
            
        Returns:
            ResultadoBusqueda con la ruta encontrada o None si no existe.
        """
        if origen not in self.grafo.nodos or destino not in self.grafo.nodos:
            return None
        
        pila = [(origen, [origen], 0.0, 0.0)]
        visitados: Set[str] = set()
        nodos_expandidos = 0
        
        while pila:
            nodo_actual, ruta, distancia, tiempo = pila.pop()
            nodos_expandidos += 1
            
            if nodo_actual == destino:
                return ResultadoBusqueda(
                    ruta=ruta,
                    distancia_total=round(distancia, 2),
                    tiempo_total=round(tiempo, 2),
                    nodos_expandidos=nodos_expandidos,
                    algoritmo="DFS"
                )
            
            if nodo_actual in visitados:
                continue
            
            visitados.add(nodo_actual)
            
            for arista in self.grafo.obtener_vecinos(nodo_actual):
                if arista.destino not in visitados:
                    nueva_ruta = ruta + [arista.destino]
                    nueva_distancia = distancia + arista.distancia
                    nuevo_tiempo = tiempo + arista.tiempo_estimado
                    pila.append((arista.destino, nueva_ruta,
                               nueva_distancia, nuevo_tiempo))
        
        return None
    
    def a_estrella(self, origen: str, destino: str) -> Optional[ResultadoBusqueda]:
        """Algoritmo A* - Búsqueda informada.
        
        Utiliza heurística de distancia euclidiana al destino.
        
        Args:
            origen: Nombre del nodo de origen.
            destino: Nombre del nodo de destino.
            
        Returns:
            ResultadoBusqueda con la ruta óptima encontrada o None.
        """
        if origen not in self.grafo.nodos or destino not in self.grafo.nodos:
            return None
        
        # Cola de prioridad: (f_score, g_score, nodo, ruta, distancia, tiempo)
        f_score = {origen: self.grafo.calcular_heuristica(origen, destino)}
        cola = [(f_score[origen], 0.0, origen, [origen], 0.0, 0.0)]
        
        g_score: Dict[str, float] = {origen: 0.0}
        visitados: Set[str] = set()
        nodos_expandidos = 0
        
        while cola:
            _, _, nodo_actual, ruta, distancia, tiempo = heapq.heappop(cola)
            nodos_expandidos += 1
            
            if nodo_actual == destino:
                return ResultadoBusqueda(
                    ruta=ruta,
                    distancia_total=round(distancia, 2),
                    tiempo_total=round(tiempo, 2),
                    nodos_expandidos=nodos_expandidos,
                    algoritmo="A*"
                )
            
            if nodo_actual in visitados:
                continue
            
            visitados.add(nodo_actual)
            
            for arista in self.grafo.obtener_vecinos(nodo_actual):
                if arista.destino in visitados:
                    continue
                
                nuevo_g = g_score[nodo_actual] + arista.tiempo_estimado
                
                if arista.destino not in g_score or nuevo_g < g_score[arista.destino]:
                    g_score[arista.destino] = nuevo_g
                    h = self.grafo.calcular_heuristica(arista.destino, destino)
                    f = nuevo_g + h
                    f_score[arista.destino] = f
                    
                    nueva_ruta = ruta + [arista.destino]
                    nueva_distancia = distancia + arista.distancia
                    nuevo_tiempo = tiempo + arista.tiempo_estimado
                    
                    heapq.heappush(cola, (f, nuevo_g, arista.destino, 
                                         nueva_ruta, nueva_distancia, nuevo_tiempo))
        
        return None
    
    def comparar_algoritmos(self, origen: str, destino: str) -> Dict[str, any]:
        """Compara los tres algoritmos de búsqueda.
        
        Args:
            origen: Nombre del nodo de origen.
            destino: Nombre del nodo de destino.
            
        Returns:
            Diccionario con resultados de BFS, DFS y A*.
        """
        resultados = {}
        
        resultado_bfs = self.bfs(origen, destino)
        if resultado_bfs:
            resultados["BFS"] = {
                "ruta": resultado_bfs.ruta,
                "distancia": resultado_bfs.distancia_total,
                "tiempo": resultado_bfs.tiempo_total,
                "nodos_expandidos": resultado_bfs.nodos_expandidos
            }
        
        resultado_dfs = self.dfs(origen, destino)
        if resultado_dfs:
            resultados["DFS"] = {
                "ruta": resultado_dfs.ruta,
                "distancia": resultado_dfs.distancia_total,
                "tiempo": resultado_dfs.tiempo_total,
                "nodos_expandidos": resultado_dfs.nodos_expandidos
            }
        
        resultado_a = self.a_estrella(origen, destino)
        if resultado_a:
            resultados["A*"] = {
                "ruta": resultado_a.ruta,
                "distancia": resultado_a.distancia_total,
                "tiempo": resultado_a.tiempo_total,
                "nodos_expandidos": resultado_a.nodos_expandidos
            }
        
        return resultados


def main():
    """Función principal para probar los algoritmos de búsqueda."""
    import sys
    sys.path.insert(0, '/workspace/backend')
    from generador_dataset import GeneradorDatasetTrafico
    
    # Generar dataset
    print("=== Generando Dataset ===")
    generador = GeneradorDatasetTrafico()
    df = generador.generar_dataset(num_registros=150)
    
    # Crear grafo
    print("\n=== Construyendo Grafo ===")
    grafo = GrafoTrafico()
    grafo.cargar_desde_dataframe(df)
    print(f"Nodos creados: {len(grafo.nodos)}")
    print(f"Aristas creadas: {sum(len(v) for v in grafo.aristas.values()) // 2}")
    
    # Seleccionar origen y destino de ejemplo
    ciudades_unicas = df["ciudad"].unique()
    ciudad_ejemplo = ciudades_unicas[0]
    calles_ciudad = df[df["ciudad"] == ciudad_ejemplo]["origen"].unique()
    
    if len(calles_ciudad) >= 2:
        origen = calles_ciudad[0]
        destino = calles_ciudad[1]
        
        print(f"\n=== Probando Búsqueda: {origen} → {destino} ===")
        print(f"Ciudad: {ciudad_ejemplo}")
        
        # Crear buscador
        buscador = BuscadorRutas(grafo)
        
        # Comparar algoritmos
        resultados = buscador.comparar_algoritmos(origen, destino)
        
        for alg, res in resultados.items():
            print(f"\n{alg}:")
            print(f"  Ruta: {' → '.join(res['ruta'][:5])}{'...' if len(res['ruta']) > 5 else ''}")
            print(f"  Distancia: {res['distancia']} km")
            print(f"  Tiempo: {res['tiempo']} min")
            print(f"  Nodos expandidos: {res['nodos_expandidos']}")
    else:
        print("No hay suficientes calles para probar la búsqueda.")


if __name__ == "__main__":
    main()
