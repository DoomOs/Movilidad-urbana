"""
Motor de Lógica de Predicados para Toma de Decisiones.

Implementación de un sistema basado en reglas tipo Prolog para
la toma de decisiones en recomendación de rutas urbanas.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class TipoRegla(Enum):
    """Tipos de reglas disponibles."""
    CONDICIONAL = "condicional"
    INFERENCIA = "inferencia"
    RESTRICCION = "restriccion"


@dataclass
class Hecho:
    """Representa un hecho en la base de conocimiento.
    
    Attributes:
        predicado: Nombre del predicado.
        argumentos: Lista de argumentos del predicado.
        valor: Valor booleano o numérico del hecho.
    """
    predicado: str
    argumentos: List[Any]
    valor: Any = True


@dataclass
class Regla:
    """Representa una regla lógica.
    
    Attributes:
        id: Identificador único de la regla.
        nombre: Nombre descriptivo de la regla.
        condicion: Función que evalúa la condición.
        accion: Función que ejecuta la acción si se cumple.
        tipo: Tipo de regla.
        prioridad: Prioridad de ejecución (1-10).
    """
    id: int
    nombre: str
    condicion: callable
    accion: callable
    tipo: TipoRegla
    prioridad: int = 5


class MotorInferencia:
    """Motor de inferencia para lógica de predicados.
    
    Simula un sistema tipo Prolog con hechos y reglas.
    
    Attributes:
        hechos: Base de hechos actuales.
        reglas: Conjunto de reglas activas.
        conclusiones: Conclusiones derivadas de las reglas.
    """
    
    def __init__(self):
        """Inicializa el motor de inferencia vacío."""
        self.hechos: Dict[str, Hecho] = {}
        self.reglas: List[Regla] = []
        self.conclusiones: Dict[str, Any] = {}
    
    def agregar_hecho(self, hecho: Hecho) -> None:
        """Agrega un hecho a la base de conocimiento.
        
        Args:
            hecho: Hecho a agregar.
        """
        clave = f"{hecho.predicado}({','.join(map(str, hecho.argumentos))})"
        self.hechos[clave] = hecho
    
    def obtener_hecho(self, predicado: str, argumentos: List[Any]) -> Optional[Hecho]:
        """Obtiene un hecho de la base de conocimiento.
        
        Args:
            predicado: Nombre del predicado.
            argumentos: Lista de argumentos.
            
        Returns:
            El hecho si existe, None en caso contrario.
        """
        clave = f"{predicado}({','.join(map(str, argumentos))})"
        return self.hechos.get(clave)
    
    def agregar_regla(self, regla: Regla) -> None:
        """Agrega una regla al motor.
        
        Args:
            regla: Regla a agregar.
        """
        self.reglas.append(regla)
        # Ordenar por prioridad (mayor prioridad primero)
        self.reglas.sort(key=lambda r: r.prioridad, reverse=True)
    
    def evaluar_condicion(self, contexto: Dict[str, Any], 
                         condicion: callable) -> bool:
        """Evalúa una condición dado un contexto.
        
        Args:
            contexto: Diccionario con variables del contexto.
            condicion: Función de condición.
            
        Returns:
            True si se cumple la condición, False en caso contrario.
        """
        try:
            return condicion(contexto)
        except Exception:
            return False
    
    def ejecutar_accion(self, contexto: Dict[str, Any], 
                       accion: callable) -> Optional[Dict[str, Any]]:
        """Ejecuta una acción dado un contexto.
        
        Args:
            contexto: Diccionario con variables del contexto.
            accion: Función de acción.
            
        Returns:
            Resultado de la acción o None.
        """
        try:
            return accion(contexto)
        except Exception:
            return None
    
    def inferir(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta el proceso de inferencia sobre todas las reglas.
        
        Args:
            contexto: Contexto actual con hechos y variables.
            
        Returns:
            Diccionario con conclusiones derivadas.
        """
        self.conclusiones = {}
        
        for regla in self.reglas:
            if self.evaluar_condicion(contexto, regla.condicion):
                resultado = self.ejecutar_accion(contexto, regla.accion)
                if resultado:
                    self.conclusiones[regla.nombre] = resultado
        
        return self.conclusiones
    
    def limpiar(self) -> None:
        """Limpia hechos y conclusiones para nueva inferencia."""
        self.conclusiones = {}


class SistemaReglasTrafico:
    """Sistema de reglas especializado para tráfico urbano.
    
    Implementa 5 reglas lógicas mínimas requeridas:
    1. Si tráfico es alto y distancia > 5km → descartar ruta
    2. Si lluvia → multiplicar tiempo por 1.5
    3. Si hora pico → evitar zonas escolares
    4. Si vehículo es bicicleta → evitar autopistas
    5. Si costo combustible alto → priorizar distancia corta
    
    Attributes:
        motor: Motor de inferencia.
    """
    
    def __init__(self):
        """Inicializa el sistema de reglas con todas las reglas definidas."""
        self.motor = MotorInferencia()
        self._inicializar_reglas()
    
    def _inicializar_reglas(self) -> None:
        """Inicializa todas las reglas del sistema."""
        
        # Regla 1: Tráfico alto + distancia larga → descartar ruta
        regla1 = Regla(
            id=1,
            nombre="evitar_trafico_alto_larga_distancia",
            condicion=lambda ctx: (
                ctx.get("trafico") == "Alto" or ctx.get("trafico") == "Muy Alto"
            ) and ctx.get("distancia", 0) > 5.0,
            accion=lambda ctx: {
                "recomendacion": "descartar_ruta",
                "razon": "Tráfico alto en ruta larga (>5km)",
                "factor_multiplicador": 2.0,
                "prioridad": "alta"
            },
            tipo=TipoRegla.RESTRICCION,
            prioridad=9
        )
        
        # Regla 2: Lluvia → ajustar tiempo
        regla2 = Regla(
            id=2,
            nombre="ajustar_tiempo_por_lluvia",
            condicion=lambda ctx: ctx.get("clima") in ["Lluvia Ligera", "Lluvia Intensa"],
            accion=lambda ctx: {
                "recomendacion": "ajustar_tiempo",
                "razon": f"Condición climática: {ctx.get('clima')}",
                "factor_multiplicador": 1.5 if ctx.get("clima") == "Lluvia Intensa" else 1.2,
                "advertencia": "Se recomienda aumentar tiempo estimado por lluvia"
            },
            tipo=TipoRegla.INFERENCIA,
            prioridad=8
        )
        
        # Regla 3: Hora pico → evitar zonas escolares
        regla3 = Regla(
            id=3,
            nombre="evitar_zonas_escolares_hora_pico",
            condicion=lambda ctx: (
                7 <= ctx.get("hora", 0) <= 9 or 
                17 <= ctx.get("hora", 0) <= 19
            ),
            accion=lambda ctx: {
                "recomendacion": "evitar_zonas_escolares",
                "razon": "Hora pico escolar detectada",
                "zonas_a_evitar": ["escuelas", "colegios", "guarderías"],
                "alternativa": "usar_rutas_secundarias"
            },
            tipo=TipoRegla.RESTRICCION,
            prioridad=7
        )
        
        # Regla 4: Bicicleta → evitar autopistas
        regla4 = Regla(
            id=4,
            nombre="bicicleta_evitar_autopistas",
            condicion=lambda ctx: ctx.get("tipo_vehiculo") == "bicicleta",
            accion=lambda ctx: {
                "recomendacion": "evitar_autopistas",
                "razon": "Vehículo no permitido en autopistas",
                "tipo_ruta_preferida": "ciclovias_calles_secundarias",
                "velocidad_promedio": 15.0
            },
            tipo=TipoRegla.RESTRICCION,
            prioridad=10
        )
        
        # Regla 5: Costo combustible alto → priorizar distancia corta
        regla5 = Regla(
            id=5,
            nombre="priorizar_distancia_corta_costo_alto",
            condicion=lambda ctx: ctx.get("costo_combustible") == "alto",
            accion=lambda ctx: {
                "recomendacion": "priorizar_distancia",
                "razon": "Optimización por costo de combustible",
                "criterio_principal": "distancia_minima",
                "ahorro_estimado": "15-20%"
            },
            tipo=TipoRegla.INFERENCIA,
            prioridad=6
        )
        
        # Regla 6: Fin de semana → tráfico reducido
        regla6 = Regla(
            id=6,
            nombre="trafico_reducido_fin_semana",
            condicion=lambda ctx: ctx.get("dia_semana") in ["Sábado", "Domingo"],
            accion=lambda ctx: {
                "recomendacion": "tiempo_optimista",
                "razon": "Menor congestión en fin de semana",
                "factor_multiplicador": 0.85,
                "nota": "Excepto en zonas comerciales/turísticas"
            },
            tipo=TipoRegla.INFERENCIA,
            prioridad=5
        )
        
        # Regla 7: Noche → mayor precaución
        regla7 = Regla(
            id=7,
            nombre="precaucion_nocturna",
            condicion=lambda ctx: 22 <= ctx.get("hora", 0) or ctx.get("hora", 0) <= 5,
            accion=lambda ctx: {
                "recomendacion": "ruta_iluminada",
                "razon": "Seguridad nocturna",
                "preferencia": "calles_principales_iluminadas",
                "advertencia": "Se recomienda viajar acompañado"
            },
            tipo=TipoRegla.RESTRICCION,
            prioridad=8
        )
        
        # Agregar todas las reglas al motor
        for regla in [regla1, regla2, regla3, regla4, regla5, regla6, regla7]:
            self.motor.agregar_regla(regla)
    
    def evaluar_contexto(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa un contexto y devuelve recomendaciones.
        
        Args:
            contexto: Diccionario con información del viaje:
                - origen: Calle de origen
                - destino: Calle de destino
                - distancia: Distancia en km
                - trafico: Nivel de tráfico
                - clima: Condición climática
                - hora: Hora del día (0-23)
                - dia_semana: Día de la semana
                - tipo_vehiculo: Tipo de vehículo
                - costo_combustible: Nivel de costo
        
        Returns:
            Diccionario con recomendaciones y ajustes.
        """
        # Validar contexto mínimo
        contexto_minimo = {
            "trafico": contexto.get("trafico", "Medio"),
            "distancia": contexto.get("distancia", 0),
            "clima": contexto.get("clima", "Despejado"),
            "hora": contexto.get("hora", 12),
            "dia_semana": contexto.get("dia_semana", "Lunes"),
            "tipo_vehiculo": contexto.get("tipo_vehiculo", "automovil"),
            "costo_combustible": contexto.get("costo_combustible", "normal")
        }
        
        # Ejecutar inferencia
        conclusiones = self.motor.inferir(contexto_minimo)
        
        # Calcular factor total de ajuste de tiempo
        factor_tiempo_total = 1.0
        recomendaciones_lista = []
        advertencias_lista = []
        
        for nombre_regla, resultado in conclusiones.items():
            if "factor_multiplicador" in resultado:
                factor_tiempo_total *= resultado["factor_multiplicador"]
            
            if "recomendacion" in resultado:
                recomendaciones_lista.append(resultado["recomendacion"])
            
            if "advertencia" in resultado:
                advertencias_lista.append(resultado["advertencia"])
        
        # Construir respuesta completa
        respuesta = {
            "contexto_evaluado": contexto_minimo,
            "reglas_activadas": list(conclusiones.keys()),
            "conclusiones": conclusiones,
            "factor_ajuste_tiempo": round(factor_tiempo_total, 2),
            "recomendaciones": recomendaciones_lista,
            "advertencias": advertencias_lista,
            "resumen": self._generar_resumen(conclusiones)
        }
        
        return respuesta
    
    def _generar_resumen(self, conclusiones: Dict[str, Any]) -> str:
        """Genera un resumen legible de las conclusiones.
        
        Args:
            conclusiones: Diccionario de conclusiones.
            
        Returns:
            String con resumen en lenguaje natural.
        """
        if not conclusiones:
            return "No se aplicaron reglas especiales. Ruta estándar recomendada."
        
        resumenes = []
        for nombre, resultado in conclusiones.items():
            if "razon" in resultado:
                resumenes.append(resultado["razon"])
        
        if resumenes:
            return "; ".join(resumenes)
        return "Se aplicaron ajustes basados en las condiciones actuales."
    
    def aplicar_reglas_a_ruta(self, ruta_info: Dict[str, Any], 
                             contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica las reglas a una ruta específica.
        
        Args:
            ruta_info: Información de la ruta (distancia, tiempo, etc.)
            contexto: Contexto del viaje.
            
        Returns:
            Ruta ajustada con recomendaciones aplicadas.
        """
        evaluacion = self.evaluar_contexto(contexto)
        
        # Copiar información de ruta
        ruta_ajustada = ruta_info.copy()
        
        # Aplicar factor de tiempo
        tiempo_original = ruta_info.get("tiempo_estimado", 0)
        tiempo_ajustado = tiempo_original * evaluacion["factor_ajuste_tiempo"]
        
        ruta_ajustada["tiempo_original"] = tiempo_original
        ruta_ajustada["tiempo_ajustado"] = round(tiempo_ajustado, 2)
        ruta_ajustada["evaluacion_logica"] = evaluacion
        
        return ruta_ajustada


def main():
    """Función principal para probar el sistema de reglas."""
    print("=== Sistema de Lógica de Predicados ===\n")
    
    sistema = SistemaReglasTrafico()
    
    # Caso de prueba 1: Viaje en hora pico con lluvia
    print("--- Caso 1: Hora pico, lluvia, automóvil ---")
    contexto1 = {
        "origen": "Av. Insurgentes Sur",
        "destino": "Av. Universidad",
        "distancia": 8.5,
        "trafico": "Alto",
        "clima": "Lluvia Ligera",
        "hora": 8,
        "dia_semana": "Martes",
        "tipo_vehiculo": "automovil",
        "costo_combustible": "normal"
    }
    
    resultado1 = sistema.evaluar_contexto(contexto1)
    print(f"Reglas activadas: {len(resultado1['reglas_activadas'])}")
    print(f"Factor de ajuste: {resultado1['factor_ajuste_tiempo']}")
    print(f"Recomendaciones: {', '.join(resultado1['recomendaciones'])}")
    print(f"Resumen: {resultado1['resumen']}\n")
    
    # Caso de prueba 2: Bicicleta en fin de semana
    print("--- Caso 2: Bicicleta, fin de semana ---")
    contexto2 = {
        "origen": "Av. Vallarta",
        "destino": "Periférico Sur",
        "distancia": 6.0,
        "trafico": "Medio",
        "clima": "Despejado",
        "hora": 10,
        "dia_semana": "Sábado",
        "tipo_vehiculo": "bicicleta",
        "costo_combustible": "no_aplica"
    }
    
    resultado2 = sistema.evaluar_contexto(contexto2)
    print(f"Reglas activadas: {len(resultado2['reglas_activadas'])}")
    print(f"Factor de ajuste: {resultado2['factor_ajuste_tiempo']}")
    print(f"Recomendaciones: {', '.join(resultado2['recomendaciones'])}")
    print(f"Resumen: {resultado2['resumen']}\n")
    
    # Caso de prueba 3: Noche, costo combustible alto
    print("--- Caso 3: Noche, costo combustible alto ---")
    contexto3 = {
        "origen": "Blvd. Díaz Ordaz",
        "destino": "Av. Constitución",
        "distancia": 12.0,
        "trafico": "Bajo",
        "clima": "Despejado",
        "hora": 23,
        "dia_semana": "Jueves",
        "tipo_vehiculo": "automovil",
        "costo_combustible": "alto"
    }
    
    resultado3 = sistema.evaluar_contexto(contexto3)
    print(f"Reglas activadas: {len(resultado3['reglas_activadas'])}")
    print(f"Factor de ajuste: {resultado3['factor_ajuste_tiempo']}")
    print(f"Recomendaciones: {', '.join(resultado3['recomendaciones'])}")
    print(f"Resumen: {resultado3['resumen']}\n")
    
    # Demostrar aplicación a ruta
    print("--- Aplicando reglas a ruta específica ---")
    ruta_ejemplo = {
        "ruta": ["Av. Insurgentes", "Av. Universidad", "Destino"],
        "distancia": 8.5,
        "tiempo_estimado": 25.0
    }
    
    ruta_ajustada = sistema.aplicar_reglas_a_ruta(ruta_ejemplo, contexto1)
    print(f"Tiempo original: {ruta_ajustada['tiempo_original']} min")
    print(f"Tiempo ajustado: {ruta_ajustada['tiempo_ajustado']} min")
    print(f"Diferencia: {ruta_ajustada['tiempo_ajustado'] - ruta_ajustada['tiempo_original']:.2f} min")


if __name__ == "__main__":
    main()
