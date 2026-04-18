"""
Generador de Dataset de Tráfico Urbano Realista.

Este módulo genera un dataset simulado de tráfico urbano con calles y ciudades
reales de ejemplo, incluyendo condiciones de tráfico, distancias y tiempos estimados.
"""

import pandas as pd
import numpy as np
import random
from typing import List, Dict, Tuple


class GeneradorDatasetTrafico:
    """Clase para generar datasets de tráfico urbano realista.
    
    Attributes:
        ciudades: Lista de ciudades principales.
        calles: Diccionario de calles por ciudad.
        condiciones_trafico: Niveles posibles de tráfico.
    """
    
    def __init__(self):
        """Inicializa el generador con datos de ciudades y calles realistas."""
        self.ciudades = [
            "Ciudad de México", "Guadalajara", "Monterrey", "Puebla", 
            "Tijuana", "León", "Juárez", "Zapopan", "Mérida", "San Luis Potosí"
        ]
        
        self.calles_por_ciudad = {
            "Ciudad de México": [
                "Av. Paseo de la Reforma", "Av. Insurgentes Sur", "Av. Universidad",
                "Blvd. Manuel Ávila Camacho", "Eje Central Lázaro Cárdenas",
                "Viaducto Miguel Alemán", "Calzada de Tlalpan", "Av. Chapultepec",
                "Periférico Norte", "Av. Revolución", "Gran Vía", "Eje 4 Sur"
            ],
            "Guadalajara": [
                "Av. Vallarta", "Av. López Mateos", "Periférico Sur",
                "Calzada Independencia", "Av. Federalismo", "Blvd. Marcelino García Barragán",
                "Av. Juárez", "Calzada del Ejército", "Av. Patria", "Anillo Periférico"
            ],
            "Monterrey": [
                "Av. Constitución", "Av. Gonzalitos", "Blvd. Díaz Ordaz",
                "Av. Lincoln", "Calzada del Valle", "Av. Morones Prieto",
                "Av. Sendero", "Blvd. Manuel J. Clouthier", "Av. Las Torres",
                "Carretera Nacional"
            ],
            "Puebla": [
                "Blvd. Hermanos Serdán", "Av. Juárez", "Recta a Cholula",
                "Vía Atlixcáyotl", "Blvd. 5 de Mayo", "Av. 14 Oriente",
                "Circuito Juan Pablo II", "Av. Forjadores de Puebla"
            ],
            "Tijuana": [
                "Blvd. Agua Caliente", "Av. Internacional", "Blvd. Sánchez Taboada",
                "Calzada Tecnológico", "Av. Revolución", "Blvd. Fundadores",
                "Vía Rápida Oriente", "Blvd. Gustavo Aubanel Vallejo"
            ],
            "León": [
                "Blvd. Adolfo López Mateos", "Blvd. Manuel Ávila Camacho",
                "Blvd. Juan José Torres Landa", "Av. Universidad",
                "Blvd. Hilario Medina", "Calzada Las Américas"
            ],
            "Juárez": [
                "Av. Tecnológico", "Av. Las Américas", "Periférico Ramón Corona",
                "Av. Plutarco Elías Calles", "Blvd. Ortiz Mena",
                "Av. Heroico Colegio Militar"
            ],
            "Zapopan": [
                "Av. Vallarta", "Periférico Norte", "Av. Moctezuma",
                "Blvd. Puerta de Hierro", "Av. Guadalupe", "Camino Arenero"
            ],
            "Mérida": [
                "Av. Colón", "Blvd. Kukulcán", "Av. Itzáes", "Calle 60",
                "Periférico Manuel Bertrán", "Av. Jacinto Canek"
            ],
            "San Luis Potosí": [
                "Av. Venustiano Carranza", "Blvd. Antonio Rocha Cordero",
                "Av. Universidad", "Blvd. Diego Zapata", "Eje 103",
                "Salida a Matehuala"
            ]
        }
        
        self.condiciones_trafico = ["Bajo", "Medio", "Alto", "Muy Alto"]
        self.condiciones_clima = ["Despejado", "Nublado", "Lluvia Ligera", "Lluvia Intensa"]
        self.horas_dia = list(range(24))
        self.dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
    def _calcular_distancia(self, calle_origen: str, calle_destino: str, 
                           ciudad: str) -> float:
        """Calcula una distancia simulada entre dos calles.
        
        Args:
            calle_origen: Nombre de la calle de origen.
            calle_destino: Nombre de la calle de destino.
            ciudad: Ciudad donde se encuentran las calles.
            
        Returns:
            Distancia en kilómetros (valor simulado entre 1.5 y 25 km).
        """
        calles = self.calles_por_ciudad.get(ciudad, [])
        if not calles or calle_origen == calle_destino:
            return round(random.uniform(1.5, 5.0), 2)
        
        idx_origen = calles.index(calle_origen) if calle_origen in calles else 0
        idx_destino = calles.index(calle_destino) if calle_destino in calles else len(calles) - 1
        
        diferencia = abs(idx_origen - idx_destino)
        distancia_base = diferencia * 2.5
        variacion = random.uniform(-1.0, 3.0)
        
        return round(max(1.5, min(25.0, distancia_base + variacion)), 2)
    
    def _calcular_tiempo(self, distancia: float, trafico: str, 
                        clima: str, hora: int) -> float:
        """Calcula el tiempo estimado de viaje basado en múltiples factores.
        
        Args:
            distancia: Distancia en kilómetros.
            trafico: Nivel de tráfico ("Bajo", "Medio", "Alto", "Muy Alto").
            clima: Condición climática actual.
            hora: Hora del día (0-23).
            
        Returns:
            Tiempo estimado en minutos.
        """
        # Velocidad base según tráfico (km/h)
        velocidades_base = {
            "Bajo": 50,
            "Medio": 35,
            "Alto": 20,
            "Muy Alto": 12
        }
        
        velocidad = velocidades_base.get(trafico, 35)
        
        # Factor por clima
        factores_clima = {
            "Despejado": 1.0,
            "Nublado": 1.05,
            "Lluvia Ligera": 1.2,
            "Lluvia Intensa": 1.5
        }
        
        factor_clima = factores_clima.get(clima, 1.0)
        
        # Factor por hora (horas pico: 7-9 AM, 6-8 PM)
        factor_hora = 1.0
        if 7 <= hora <= 9 or 18 <= hora <= 20:
            factor_hora = 1.3
        elif 10 <= hora <= 16:
            factor_hora = 1.1
        elif 21 <= hora or hora <= 5:
            factor_hora = 0.9
        
        # Calcular tiempo en minutos
        tiempo_horas = distancia / (velocidad * factor_clima * factor_hora)
        tiempo_minutos = tiempo_horas * 60
        
        # Añadir variación aleatoria (±10%)
        variacion = random.uniform(0.9, 1.1)
        tiempo_final = tiempo_minutos * variacion
        
        return round(tiempo_final, 2)
    
    def _determinar_trafico(self, hora: int, dia: str) -> str:
        """Determina el nivel de tráfico basado en hora y día.
        
        Args:
            hora: Hora del día (0-23).
            dia: Día de la semana.
            
        Returns:
            Nivel de tráfico como string.
        """
        # Horarios pico
        horas_pico_manana = [7, 8, 9]
        horas_pico_tarde = [17, 18, 19, 20]
        
        es_fin_de_semana = dia in ["Sábado", "Domingo"]
        
        if not es_fin_de_semana:
            if hora in horas_pico_manana or hora in horas_pico_tarde:
                return random.choice(["Alto", "Muy Alto"])
            elif 10 <= hora <= 16:
                return random.choice(["Medio", "Alto"])
            else:
                return random.choice(["Bajo", "Medio"])
        else:
            if 11 <= hora <= 21:
                return random.choice(["Medio", "Alto"])
            else:
                return "Bajo"
    
    def generar_dataset(self, num_registros: int = 150) -> pd.DataFrame:
        """Genera el dataset completo de tráfico urbano.
        
        Args:
            num_registros: Número de registros a generar (mínimo 50, máximo 500).
            
        Returns:
            DataFrame de pandas con el dataset generado.
            
        Raises:
            ValueError: Si num_registros está fuera del rango permitido.
        """
        if num_registros < 50 or num_registros > 500:
            raise ValueError("El número de registros debe estar entre 50 y 500")
        
        datos = []
        
        for i in range(num_registros):
            # Seleccionar ciudad aleatoria
            ciudad = random.choice(self.ciudades)
            calles_disponibles = self.calles_por_ciudad[ciudad]
            
            # Seleccionar calles de origen y destino diferentes
            if len(calles_disponibles) >= 2:
                calle_origen, calle_destino = random.sample(calles_disponibles, 2)
            else:
                continue
            
            # Generar atributos temporales
            dia = random.choice(self.dias_semana)
            hora = random.choice(self.horas_dia)
            
            # Determinar tráfico basado en hora y día
            trafico = self._determinar_trafico(hora, dia)
            
            # Calcular distancia
            distancia = self._calcular_distancia(calle_origen, calle_destino, ciudad)
            
            # Seleccionar clima
            clima = random.choice(self.condiciones_clima)
            
            # Calcular tiempo estimado
            tiempo = self._calcular_tiempo(distancia, trafico, clima, hora)
            
            # Crear registro
            registro = {
                "id": i + 1,
                "origen": calle_origen,
                "destino": calle_destino,
                "ciudad": ciudad,
                "distancia_km": distancia,
                "trafico": trafico,
                "clima": clima,
                "hora": hora,
                "dia_semana": dia,
                "tiempo_estimado_min": tiempo,
                "fecha_registro": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
            }
            
            datos.append(registro)
        
        df = pd.DataFrame(datos)
        return df
    
    def guardar_dataset(self, df: pd.DataFrame, ruta_archivo: str) -> None:
        """Guarda el dataset en formato CSV.
        
        Args:
            df: DataFrame de pandas con los datos.
            ruta_archivo: Ruta completa del archivo a guardar.
        """
        df.to_csv(ruta_archivo, index=False, encoding='utf-8')
        print(f"Dataset guardado exitosamente en: {ruta_archivo}")
    
    def analizar_dataset(self, df: pd.DataFrame) -> Dict[str, any]:
        """Realiza un análisis exploratorio básico del dataset.
        
        Args:
            df: DataFrame de pandas con los datos.
            
        Returns:
            Diccionario con estadísticas descriptivas del dataset.
        """
        analisis = {
            "total_registros": len(df),
            "ciudades": df["ciudad"].nunique(),
            "distancia_promedio": round(df["distancia_km"].mean(), 2),
            "tiempo_promedio": round(df["tiempo_estimado_min"].mean(), 2),
            "trafico_mas_frecuente": df["trafico"].mode()[0],
            "clima_mas_frecuente": df["clima"].mode()[0],
            "hora_pico": df.groupby("hora")["tiempo_estimado_min"].mean().idxmax(),
            "dia_mas_congestionado": df.groupby("dia_semana")["tiempo_estimado_min"].mean().idxmax()
        }
        
        return analisis


def main():
    """Función principal para generar y guardar el dataset."""
    generador = GeneradorDatasetTrafico()
    
    # Generar dataset con 150 registros
    print("Generando dataset de tráfico urbano...")
    df = generador.generar_dataset(num_registros=150)
    
    # Guardar dataset
    ruta_guardado = "datasets/trafico_urbano.csv"
    generador.guardar_dataset(df, ruta_guardado)
    
    # Realizar análisis exploratorio
    print("\n=== Análisis Exploratorio del Dataset ===")
    analisis = generador.analizar_dataset(df)
    
    for clave, valor in analisis.items():
        print(f"{clave.replace('_', ' ').title()}: {valor}")
    
    # Mostrar primeras filas
    print("\n=== Primeras 10 filas del dataset ===")
    print(df.head(10).to_string())
    
    # Estadísticas descriptivas
    print("\n=== Estadísticas Descriptivas ===")
    print(df[["distancia_km", "tiempo_estimado_min"]].describe())
    
    return df


if __name__ == "__main__":
    main()
