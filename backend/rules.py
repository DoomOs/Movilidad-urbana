"""
Motor de reglas de lógica de predicados para decisiones de tráfico.
Implementa 7+ reglas tipo Prolog para ajustar recomendaciones.
"""
from typing import Dict, List, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import math


class TipoRegla(str, Enum):
    """Tipos de reglas."""
    RESTRICCION = "restriccion"      # Puede descartar rutas
    INFERENCIA = "inferencia"         # Modifica tiempos/recomendaciones
    CONDICIONAL = "condicional"       # Cambia comportamiento


@dataclass
class ResultadoRegla:
    """Resultado de evaluar una regla."""
    nombre: str
    aplicable: bool
    recomendacion: str
    razon: str
    factor_tiempo: float = 1.0
    advertencias: List[str] = field(default_factory=list)
    prioridad: int = 5


class Regla:
    """Una regla individual del sistema."""

    def __init__(
        self,
        id: int,
        nombre: str,
        condicion: Callable[[Dict], bool],
        accion: Callable[[Dict], ResultadoRegla],
        tipo: TipoRegla = TipoRegla.INFERENCIA,
        prioridad: int = 5
    ):
        self.id = id
        self.nombre = nombre
        self.condicion = condicion
        self.accion = accion
        self.tipo = tipo
        self.prioridad = prioridad

    def evaluar(self, contexto: Dict) -> ResultadoRegla:
        """Evaluar esta regla con el contexto dado."""
        try:
            if self.condicion(contexto):
                return self.accion(contexto)
            return ResultadoRegla(
                nombre=self.nombre,
                aplicable=False,
                recomendacion="ninguna",
                razon="Condición no cumplida"
            )
        except Exception as e:
            return ResultadoRegla(
                nombre=self.nombre,
                aplicable=False,
                recomendacion="ninguna",
                razon=f"Error en evaluación: {str(e)}"
            )


class MotorReglas:
    """Motor de inferencia para reglas de tráfico."""

    def __init__(self):
        self.reglas: List[Regla] = []
        self._inicializar_reglas()

    def _inicializar_reglas(self):
        """Crear las 7+ reglas del sistema."""

        # ==========================================================
        # REGLA 1: Tráfico alto + distancia larga → descartar
        # ==========================================================
        regla1 = Regla(
            id=1,
            nombre="evitar_trafico_alto_larga_distancia",
            condicion=lambda ctx: (
                ctx.get("trafico") in ["Alto", "Muy Alto"] and
                ctx.get("distancia", 0) > 5.0
            ),
            accion=lambda ctx: ResultadoRegla(
                nombre="evitar_trafico_alto_larga_distancia",
                aplicable=True,
                recomendacion="descartar_ruta",
                razon=f"Tráfico {ctx.get('trafico')} en ruta de {ctx.get('distancia')}km",
                factor_tiempo=2.0,
                advertencias=["Considerar ruta alternativa"],
                prioridad=9
            ),
            tipo=TipoRegla.RESTRICCION,
            prioridad=9
        )

        # ==========================================================
        # REGLA 2: Lluvia → ajustar tiempo
        # ==========================================================
        regla2 = Regla(
            id=2,
            nombre="ajustar_tiempo_por_lluvia",
            condicion=lambda ctx: ctx.get("clima") in ["Lluvia Ligera", "Lluvia Intensa"],
            accion=lambda ctx: ResultadoRegla(
                nombre="ajustar_tiempo_por_lluvia",
                aplicable=True,
                recomendacion="ajustar_tiempo",
                razon=f"Condición climática: {ctx.get('clima')}",
                factor_tiempo=1.5 if ctx.get("clima") == "Lluvia Intensa" else 1.2,
                advertencias=["Reducir velocidad", "Mantener distancia de seguridad"],
                prioridad=8
            ),
            tipo=TipoRegla.INFERENCIA,
            prioridad=8
        )

        # ==========================================================
        # REGLA 3: Hora pico → evitar zonas escolares
        # ==========================================================
        regla3 = Regla(
            id=3,
            nombre="evitar_zonas_escolares_hora_pico",
            condicion=lambda ctx: (
                (7 <= ctx.get("hora", 0) <= 9) or
                (17 <= ctx.get("hora", 0) <= 19)
            ),
            accion=lambda ctx: ResultadoRegla(
                nombre="evitar_zonas_escolares_hora_pico",
                aplicable=True,
                recomendacion="evitar_zonas_escolares",
                razon="Hora pico escolar detectada",
                factor_tiempo=1.15,
                advertencias=["Zonas escolares activas", "Mayor congestión vial"],
                prioridad=7
            ),
            tipo=TipoRegla.RESTRICCION,
            prioridad=7
        )

        # ==========================================================
        # REGLA 4: Bicicleta → evitar autopistas
        # ==========================================================
        regla4 = Regla(
            id=4,
            nombre="bicicleta_evitar_autopistas",
            condicion=lambda ctx: ctx.get("vehiculo") == "bicicleta",
            accion=lambda ctx: ResultadoRegla(
                nombre="bicicleta_evitar_autopistas",
                aplicable=True,
                recomendacion="evitar_autopistas",
                razon="Vehículo no permitido en autopistas",
                factor_tiempo=1.0,
                advertencias=["Usar ciclovías", "Calles secundarias preferidas"],
                prioridad=10
            ),
            tipo=TipoRegla.RESTRICCION,
            prioridad=10
        )

        # ==========================================================
        # REGLA 5: Costo combustible alto → priorizar distancia corta
        # ==========================================================
        regla5 = Regla(
            id=5,
            nombre="priorizar_distancia_corta",
            condicion=lambda ctx: ctx.get("combustible") == "alto",
            accion=lambda ctx: ResultadoRegla(
                nombre="priorizar_distancia_corta",
                aplicable=True,
                recomendacion="priorizar_distancia",
                razon="Optimización por costo de combustible",
                factor_tiempo=0.95,
                advertencias=["Buscar ruta más corta", "Ahorro estimado 15-20%"],
                prioridad=6
            ),
            tipo=TipoRegla.INFERENCIA,
            prioridad=6
        )

        # ==========================================================
        # REGLA 6: Fin de semana → tráfico reducido
        # ==========================================================
        regla6 = Regla(
            id=6,
            nombre="trafico_reducido_fin_semana",
            condicion=lambda ctx: ctx.get("dia") in ["Sábado", "Domingo"],
            accion=lambda ctx: ResultadoRegla(
                nombre="trafico_reducido_fin_semana",
                aplicable=True,
                recomendacion="tiempo_optimista",
                razon="Menor congestión en fin de semana",
                factor_tiempo=0.85,
                advertencias=["Excepto zonas comerciales/turísticas"],
                prioridad=5
            ),
            tipo=TipoRegla.INFERENCIA,
            prioridad=5
        )

        # ==========================================================
        # REGLA 7: Noche → mayor precaución
        # ==========================================================
        regla7 = Regla(
            id=7,
            nombre="precaucion_nocturna",
            condicion=lambda ctx: (22 <= ctx.get("hora", 0) or ctx.get("hora", 0) <= 5),
            accion=lambda ctx: ResultadoRegla(
                nombre="precaucion_nocturna",
                aplicable=True,
                recomendacion="ruta_iluminada",
                razon="Seguridad nocturna",
                factor_tiempo=1.1,
                advertencias=["Iluminación vial", "Viajar acompañado"],
                prioridad=8
            ),
            tipo=TipoRegla.RESTRICCION,
            prioridad=8
        )

        # ==========================================================
        # REGLA 8: Tráfico muy alto → probabilidad de demora
        # ==========================================================
        regla8 = Regla(
            id=8,
            nombre="demora_trafico_muy_alto",
            condicion=lambda ctx: ctx.get("trafico") == "Muy Alto",
            accion=lambda ctx: ResultadoRegla(
                nombre="demora_trafico_muy_alto",
                aplicable=True,
                recomendacion="considerar_alternativa",
                razon="Tráfico extremadamente congestionado",
                factor_tiempo=1.8,
                advertencias=["Posibles desvíos", "Retrasos significativos"],
                prioridad=9
            ),
            tipo=TipoRegla.INFERENCIA,
            prioridad=9
        )

        # Agregar todas las reglas
        for regla in [regla1, regla2, regla3, regla4, regla5, regla6, regla7, regla8]:
            self.reglas.append(regla)

        # Ordenar por prioridad (mayor primero)
        self.reglas.sort(key=lambda r: r.prioridad, reverse=True)

    def evaluar(self, contexto: Dict) -> Dict[str, Any]:
        """Evaluar todas las reglas con el contexto dado.

        Args:
            contexto: Dict con:
                - trafico: str (Bajo, Medio, Alto, Muy Alto)
                - distancia: float (km)
                - clima: str (Despejado, Nublado, Lluvia Ligera, Lluvia Intensa)
                - hora: int (0-23)
                - dia: str (Lunes, Martes, etc.)
                - vehiculo: str (automovil, bicicleta, etc.)
                - combustible: str (normal, alto)

        Returns:
            Dict con recomendaciones, factor de tiempo, advertencias
        """
        # Normalizar contexto
        ctx = {
            "trafico": contexto.get("trafico", "Medio"),
            "distancia": contexto.get("distancia", 0),
            "clima": contexto.get("clima", "Despejado"),
            "hora": contexto.get("hora", 12),
            "dia": contexto.get("dia", "Lunes"),
            "vehiculo": contexto.get("vehiculo", "automovil"),
            "combustible": contexto.get("combustible", "normal")
        }

        reglas_aplicadas = []
        factor_tiempo_total = 1.0
        advertencias = []
        recomendaciones = []

        for regla in self.reglas:
            resultado = regla.evaluar(ctx)
            if resultado.aplicable:
                reglas_aplicadas.append(resultado.nombre)
                factor_tiempo_total *= resultado.factor_tiempo
                advertencias.extend(resultado.advertencias)
                recomendaciones.append(resultado.recomendacion)

        # Eliminar advertencias duplicadas
        advertencias = list(set(advertencias))

        return {
            "reglas_activadas": reglas_aplicadas,
            "factor_tiempo": round(factor_tiempo_total, 2),
            "advertencias": advertencias,
            "recomendaciones": recomendaciones,
            "resumen": self._generar_resumen(reglas_aplicadas, factor_tiempo_total)
        }

    def _generar_resumen(self, reglas: List[str], factor: float) -> str:
        """Generar resumen textual de las reglas activadas."""
        if not reglas:
            return "Sin condiciones especiales. Ruta estándar recomendada."

        resumenes = []
        for nombre in reglas:
            if "trafico_alto" in nombre:
                resumenes.append("Tráfico alto detectado")
            elif "lluvia" in nombre:
                resumenes.append("Ajuste por clima")
            elif "escolares" in nombre:
                resumenes.append("Hora pico escolar")
            elif "bicicleta" in nombre:
                resumenes.append("Restricción para bicicleta")
            elif "combustible" in nombre:
                resumenes.append("Optimización por costo")
            elif "fin_semana" in nombre:
                resumenes.append("Tráfico reducido fin de semana")
            elif "nocturna" in nombre:
                resumenes.append("Precaución nocturna")
            elif "muy_alto" in nombre:
                resumenes.append("Congestión extrema")

        if factor != 1.0:
            if factor > 1:
                resumenes.append(f"Tiempo ajustado x{factor:.1f}")
            else:
                resumenes.append(f"Tiempo reducido x{factor:.2f}")

        return "; ".join(resumenes)


def evaluar_ruta(tiempo_base: float, contexto: Dict) -> Dict[str, Any]:
    """Función helper para evaluar una ruta completa.

    Args:
        tiempo_base: Tiempo estimado base en minutos
        contexto: Contexto de evaluación

    Returns:
        Dict con tiempo ajustado y razones
    """
    motor = MotorReglas()
    resultado = motor.evaluar(contexto)

    tiempo_ajustado = tiempo_base * resultado["factor_tiempo"]

    return {
        "tiempo_base": tiempo_base,
        "tiempo_ajustado": round(tiempo_ajustado, 2),
        "factor_aplicado": resultado["factor_tiempo"],
        "reglas_activadas": resultado["reglas_activadas"],
        "advertencias": resultado["advertencias"],
        "resumen": resultado["resumen"]
    }