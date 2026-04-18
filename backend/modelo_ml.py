"""
Modelo de Machine Learning para Predicción de Tiempo de Viaje.

Implementación de modelos de regresión para predecir el tiempo estimado
de viaje basado en distancia, tráfico y otras condiciones.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
import pickle
import os


@dataclass
class MetricasEvaluacion:
    """Métricas de evaluación del modelo.
    
    Attributes:
        mae: Error absoluto medio.
        mse: Error cuadrático medio.
        rmse: Raíz del error cuadrático medio.
        r2: Coeficiente de determinación.
    """
    mae: float
    mse: float
    rmse: float
    r2: float


class ModeloPrediccionTiempo:
    """Modelo de Machine Learning para predicción de tiempo de viaje.
    
    Implementa Regresión Lineal Múltiple desde cero (sin scikit-learn)
    para cumplir con requisitos educativos del proyecto.
    
    Attributes:
        coeficientes: Coeficientes del modelo de regresión.
        intercepto: Término independiente.
        entrenado: Indica si el modelo ha sido entrenado.
        caracteristicas: Lista de nombres de características usadas.
    """
    
    def __init__(self):
        """Inicializa el modelo sin entrenar."""
        self.coeficientes: Optional[np.ndarray] = None
        self.intercepto: float = 0.0
        self.entrenado = False
        self.caracteristicas: List[str] = []
        self.medias: Optional[np.ndarray] = None
        self.std: Optional[np.ndarray] = None
    
    def _preprocesar_datos(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Normaliza los datos de entrada.
        
        Args:
            X: Matriz de características.
            
        Returns:
            Tupla con datos normalizados, medias y desviaciones estándar.
        """
        medias = np.mean(X, axis=0)
        std = np.std(X, axis=0)
        
        # Evitar división por cero
        std[std == 0] = 1
        
        X_normalizado = (X - medias) / std
        
        return X_normalizado, medias, std
    
    def _agregar_columna_unos(self, X: np.ndarray) -> np.ndarray:
        """Agrega columna de unos para el término intercepto.
        
        Args:
            X: Matriz de características.
            
        Returns:
            Matriz con columna de unos agregada.
        """
        return np.column_stack([np.ones(X.shape[0]), X])
    
    def _ecuacion_normal(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Calcula coeficientes usando ecuación normal.
        
        β = (X^T · X)^(-1) · X^T · y
        
        Args:
            X: Matriz de características con columna de unos.
            y: Vector de valores objetivo.
            
        Returns:
            Vector de coeficientes.
        """
        # X^T · X
        xt_x = X.T @ X
        
        # (X^T · X)^(-1)
        try:
            xt_x_inv = np.linalg.inv(xt_x)
        except np.linalg.LinAlgError:
            # Si no es invertible, usar pseudo-inversa
            xt_x_inv = np.linalg.pinv(xt_x)
        
        # X^T · y
        xt_y = X.T @ y
        
        # β = (X^T · X)^(-1) · X^T · y
        coeficientes = xt_x_inv @ xt_y
        
        return coeficientes
    
    def entrenar(self, df: pd.DataFrame, 
                 columnas_caracteristicas: List[str],
                 columna_objetivo: str) -> Dict[str, float]:
        """Entrena el modelo con un DataFrame.
        
        Args:
            df: DataFrame de pandas con los datos.
            columnas_caracteristicas: Lista de nombres de columnas a usar como características.
            columna_objetivo: Nombre de la columna objetivo.
            
        Returns:
            Diccionario con métricas de entrenamiento.
        """
        # Extraer características y objetivo
        X = df[columnas_caracteristicas].values
        y = df[columna_objetivo].values
        
        # Guardar nombres de características
        self.caracteristicas = columnas_caracteristicas.copy()
        
        # Normalizar características
        X_norm, medias, std = self._preprocesar_datos(X)
        self.medias = medias
        self.std = std
        
        # Agregar columna de unos
        X_bias = self._agregar_columna_unos(X_norm)
        
        # Calcular coeficientes con ecuación normal
        coeficientes_completos = self._ecuacion_normal(X_bias, y)
        
        # Separar intercepto y coeficientes
        self.intercepto = coeficientes_completos[0]
        self.coeficientes = coeficientes_completos[1:]
        
        self.entrenado = True
        
        # Calcular métricas en datos de entrenamiento
        predicciones = self.predecir_desde_dataframe(df, columnas_caracteristicas)
        metricas = self._calcular_metricas(y, predicciones)
        
        return {
            "intercepto": self.intercepto,
            "coeficientes": dict(zip(self.caracteristicas, self.coeficientes)),
            "metricas_entrenamiento": {
                "mae": metricas.mae,
                "mse": metricas.mse,
                "rmse": metricas.rmse,
                "r2": metricas.r2
            }
        }
    
    def predecir(self, X: np.ndarray) -> np.ndarray:
        """Realiza predicciones con datos normalizados.
        
        Args:
            X: Matriz de características ya normalizadas.
            
        Returns:
            Array con predicciones.
            
        Raises:
            ValueError: Si el modelo no ha sido entrenado.
        """
        if not self.entrenado:
            raise ValueError("El modelo debe ser entrenado antes de hacer predicciones")
        
        # Normalizar usando parámetros de entrenamiento
        X_norm = (X - self.medias) / self.std
        
        # Agregar columna de unos
        X_bias = self._agregar_columna_unos(X_norm)
        
        # Predecir: y = β0 + β1·x1 + β2·x2 + ...
        predicciones = X_bias @ np.concatenate([[self.intercepto], self.coeficientes])
        
        return predicciones
    
    def predecir_desde_dataframe(self, df: pd.DataFrame,
                                 columnas_caracteristicas: List[str]) -> np.ndarray:
        """Realiza predicciones desde un DataFrame.
        
        Args:
            df: DataFrame con los datos.
            columnas_caracteristicas: Columnas a usar como características.
            
        Returns:
            Array con predicciones.
        """
        X = df[columnas_caracteristicas].values
        return self.predecir(X)
    
    def predecir_individual(self, **kwargs) -> float:
        """Realiza una predicción individual.
        
        Args:
            **kwargs: Pares nombre=valor para cada característica.
            
        Returns:
            Predicción individual.
        """
        if not self.entrenado:
            raise ValueError("El modelo debe ser entrenado antes de hacer predicciones")
        
        # Crear vector de características en orden correcto
        X = np.array([[kwargs.get(car, 0) for car in self.caracteristicas]])
        
        predicciones = self.predecir(X)
        return float(predicciones[0])
    
    def _calcular_metricas(self, y_real: np.ndarray, 
                          y_pred: np.ndarray) -> MetricasEvaluacion:
        """Calcula métricas de evaluación del modelo.
        
        Args:
            y_real: Valores reales.
            y_pred: Valores predichos.
            
        Returns:
            Objeto MetricasEvaluacion con todas las métricas.
        """
        # Error absoluto medio (MAE)
        mae = np.mean(np.abs(y_real - y_pred))
        
        # Error cuadrático medio (MSE)
        mse = np.mean((y_real - y_pred) ** 2)
        
        # Raíz del error cuadrático medio (RMSE)
        rmse = np.sqrt(mse)
        
        # Coeficiente de determinación (R²)
        ss_res = np.sum((y_real - y_pred) ** 2)
        ss_tot = np.sum((y_real - np.mean(y_real)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return MetricasEvaluacion(mae=mae, mse=mse, rmse=rmse, r2=r2)
    
    def evaluar(self, df: pd.DataFrame,
               columnas_caracteristicas: List[str],
               columna_objetivo: str) -> MetricasEvaluacion:
        """Evalúa el modelo con un conjunto de datos.
        
        Args:
            df: DataFrame con los datos de prueba.
            columnas_caracteristicas: Columnas a usar como características.
            columna_objetivo: Columna objetivo real.
            
        Returns:
            Métricas de evaluación.
        """
        y_real = df[columna_objetivo].values
        y_pred = self.predecir_desde_dataframe(df, columnas_caracteristicas)
        
        return self._calcular_metricas(y_real, y_pred)
    
    def guardar_modelo(self, ruta_archivo: str) -> None:
        """Guarda el modelo entrenado en un archivo.
        
        Args:
            ruta_archivo: Ruta completa del archivo.
        """
        if not self.entrenado:
            raise ValueError("No se puede guardar un modelo no entrenado")
        
        datos_modelo = {
            "coeficientes": self.coeficientes,
            "intercepto": self.intercepto,
            "caracteristicas": self.caracteristicas,
            "medias": self.medias,
            "std": self.std,
            "entrenado": self.entrenado
        }
        
        with open(ruta_archivo, 'wb') as f:
            pickle.dump(datos_modelo, f)
        
        print(f"Modelo guardado exitosamente en: {ruta_archivo}")
    
    @classmethod
    def cargar_modelo(cls, ruta_archivo: str) -> 'ModeloPrediccionTiempo':
        """Carga un modelo guardado desde un archivo.
        
        Args:
            ruta_archivo: Ruta del archivo del modelo.
            
        Returns:
            Instancia del modelo cargado.
        """
        with open(ruta_archivo, 'rb') as f:
            datos_modelo = pickle.load(f)
        
        modelo = cls()
        modelo.coeficientes = datos_modelo["coeficientes"]
        modelo.intercepto = datos_modelo["intercepto"]
        modelo.caracteristicas = datos_modelo["caracteristicas"]
        modelo.medias = datos_modelo["medias"]
        modelo.std = datos_modelo["std"]
        modelo.entrenado = datos_modelo["entrenado"]
        
        print(f"Modelo cargado exitosamente desde: {ruta_archivo}")
        return modelo
    
    def obtener_importancia_caracteristicas(self) -> Dict[str, float]:
        """Obtiene la importancia relativa de cada característica.
        
        Returns:
            Diccionario con importancia normalizada de cada característica.
        """
        if not self.entrenado:
            return {}
        
        # Usar valor absoluto de coeficientes como importancia
        importancia = np.abs(self.coeficientes)
        importancia_total = np.sum(importancia)
        
        if importancia_total == 0:
            return {car: 0.0 for car in self.caracteristicas}
        
        importancia_normalizada = importancia / importancia_total
        
        return dict(zip(self.caracteristicas, importancia_normalizada))


def main():
    """Función principal para entrenar y evaluar el modelo."""
    import sys
    sys.path.insert(0, '/workspace/backend')
    from generador_dataset import GeneradorDatasetTrafico
    
    print("=== Modelo de Machine Learning - Predicción de Tiempo ===\n")
    
    # Generar dataset más grande para entrenamiento
    print("Generando dataset para entrenamiento...")
    generador = GeneradorDatasetTrafico()
    df = generador.generar_dataset(num_registros=300)
    
    # Dividir en entrenamiento y prueba (80/20)
    df_mezclado = df.sample(frac=1, random_state=42).reset_index(drop=True)
    tamano_entrenamiento = int(len(df_mezclado) * 0.8)
    
    df_entrenamiento = df_mezclado[:tamano_entrenamiento]
    df_prueba = df_mezclado[tamano_entrenamiento:]
    
    print(f"Registros de entrenamiento: {len(df_entrenamiento)}")
    print(f"Registros de prueba: {len(df_prueba)}\n")
    
    # Codificar variables categóricas
    print("Preprocesando datos...")
    
    # Codificar tráfico
    mapa_trafico = {"Bajo": 1, "Medio": 2, "Alto": 3, "Muy Alto": 4}
    df_entrenamiento["trafico_codificado"] = df_entrenamiento["trafico"].map(mapa_trafico)
    df_prueba["trafico_codificado"] = df_prueba["trafico"].map(mapa_trafico)
    
    # Codificar clima
    mapa_clima = {"Despejado": 1, "Nublado": 2, "Lluvia Ligera": 3, "Lluvia Intensa": 4}
    df_entrenamiento["clima_codificado"] = df_entrenamiento["clima"].map(mapa_clima)
    df_prueba["clima_codificado"] = df_prueba["clima"].map(mapa_clima)
    
    # Definir características
    caracteristicas = ["distancia_km", "trafico_codificado", "hora"]
    objetivo = "tiempo_estimado_min"
    
    # Crear y entrenar modelo
    print("\nEntrenando modelo de regresión lineal...")
    modelo = ModeloPrediccionTiempo()
    
    resultados_entrenamiento = modelo.entrenar(
        df_entrenamiento,
        caracteristicas,
        objetivo
    )
    
    print("\n=== Resultados del Entrenamiento ===")
    print(f"Intercepto: {resultados_entrenamiento['intercepto']:.4f}")
    print("\nCoeficientes:")
    for car, coef in resultados_entrenamiento['coeficientes'].items():
        print(f"  {car}: {coef:.4f}")
    
    print("\nMétricas en entrenamiento:")
    metricas_ent = resultados_entrenamiento['metricas_entrenamiento']
    print(f"  MAE: {metricas_ent['mae']:.4f} minutos")
    print(f"  RMSE: {metricas_ent['rmse']:.4f} minutos")
    print(f"  R²: {metricas_ent['r2']:.4f}")
    
    # Evaluar en conjunto de prueba
    print("\n=== Evaluación en Conjunto de Prueba ===")
    metricas_prueba = modelo.evaluar(df_prueba, caracteristicas, objetivo)
    print(f"MAE: {metricas_prueba.mae:.4f} minutos")
    print(f"MSE: {metricas_prueba.mse:.4f}")
    print(f"RMSE: {metricas_prueba.rmse:.4f} minutos")
    print(f"R²: {metricas_prueba.r2:.4f}")
    
    # Importancia de características
    print("\n=== Importancia de Características ===")
    importancia = modelo.obtener_importancia_caracteristicas()
    for car, imp in sorted(importancia.items(), key=lambda x: x[1], reverse=True):
        print(f"  {car}: {imp*100:.2f}%")
    
    # Predicciones de ejemplo
    print("\n=== Predicciones de Ejemplo ===")
    
    ejemplos = [
        {"distancia_km": 5.0, "trafico_codificado": 2, "hora": 10},
        {"distancia_km": 10.0, "trafico_codificado": 4, "hora": 18},
        {"distancia_km": 3.0, "trafico_codificado": 1, "hora": 22}
    ]
    
    for i, ejemplo in enumerate(ejemplos, 1):
        prediccion = modelo.predecir_individual(**ejemplo)
        print(f"\nEjemplo {i}:")
        print(f"  Distancia: {ejemplo['distancia_km']} km")
        print(f"  Tráfico: {ejemplo['trafico_codificado']} (1=Bajo, 4=Muy Alto)")
        print(f"  Hora: {ejemplo['hora']}:00")
        print(f"  Tiempo predicho: {prediccion:.2f} minutos")
    
    # Guardar modelo
    ruta_modelo = "backend/modelo_prediccion.pkl"
    modelo.guardar_modelo(ruta_modelo)
    
    print("\n=== Modelo listo para usar ===")
    
    return modelo


if __name__ == "__main__":
    main()
