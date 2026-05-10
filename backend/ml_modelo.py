"""
Módulo de Machine Learning para predicción de tiempo de viaje.
Usa scikit-learn con múltiples modelos: Regresión Lineal, Random Forest y XGBoost.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import joblib
import os

# Intentar importar sklearn - puede no estar instalado, usar fallback
try:
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import cross_val_score, KFold
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

from database import SessionLocal
from models import RegistroTrafico, ModeloML


@dataclass
class MetricasModelo:
    """Métricas de evaluación de un modelo."""
    mae: float
    mse: float
    rmse: float
    r2: float
    cv_scores: Optional[List[float]] = None
    cv_mean: Optional[float] = None
    cv_std: Optional[float] = None


class ModeloPredictor:
    """Clase wrapper para manejar múltiples modelos ML."""

    def __init__(self):
        self.modelos = {}
        self.modelos_info = {}
        self.scaler = StandardScaler() if HAS_SKLEARN else None
        self.entrenado = False
        self.caracteristicas = ["distancia_km", "trafico_cod", "hora", "dia_cod"]
        self.target = "tiempo_estimado_min"

    def _codificar_trafico(self, trafico_str: str) -> int:
        """Codificar nivel de tráfico a número."""
        mapa = {"Bajo": 1, "Medio": 2, "Alto": 3, "Muy Alto": 4}
        return mapa.get(trafico_str, 2)

    def _codificar_dia(self, dia: str) -> int:
        """Codificar día de la semana a número."""
        dias = {"Lunes": 1, "Martes": 2, "Miércoles": 3, "Jueves": 4,
                "Viernes": 5, "Sábado": 6, "Domingo": 7}
        return dias.get(dia, 1)

    def cargar_datos_entrenamiento(self) -> pd.DataFrame:
        """Cargar datos desde la base de datos."""
        db = SessionLocal()
        try:
            registros = db.query(RegistroTrafico).all()
            datos = []

            for r in registros:
                datos.append({
                    "distancia_km": r.distancia_km,
                    "trafico_cod": self._codificar_trafico(r.trafico.value if hasattr(r.trafico, 'value') else r.trafico),
                    "hora": r.hora,
                    "dia_cod": self._codificar_dia(r.dia_semana.value if hasattr(r.dia_semana, 'value') else r.dia_semana),
                    "tiempo_estimado_min": r.tiempo_estimado_min
                })

            return pd.DataFrame(datos)
        finally:
            db.close()

    def entrenar(self) -> Dict[str, MetricasModelo]:
        """Entrenar todos los modelos disponibles."""
        if not HAS_SKLEARN:
            print("scikit-learn no está instalado. Solo disponible regresión manual.")
            return {}

        print("Cargando datos de entrenamiento...")
        df = self.cargar_datos_entrenamiento()
        print(f"  {len(df)} registros cargados.")

        X = df[self.caracteristicas].values
        y = df[self.target].values

        # Escalar características
        X_scaled = self.scaler.fit_transform(X)

        resultados = {}

        # 1. Regresión Lineal
        print("\nEntrenando Regresión Lineal...")
        lr = LinearRegression()
        lr.fit(X_scaled, y)
        self.modelos["regresion_lineal"] = lr

        metricas_lr = self._evaluar_modelo(lr, X_scaled, y, "Regresión Lineal")
        resultados["regresion_lineal"] = metricas_lr
        self.modelos_info["regresion_lineal"] = {
            "tipo": "regresion",
            "metricas": metricas_lr
        }

        # 2. Random Forest
        print("Entrenando Random Forest...")
        rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
        rf.fit(X_scaled, y)
        self.modelos["random_forest"] = rf

        metricas_rf = self._evaluar_modelo(rf, X_scaled, y, "Random Forest")
        resultados["random_forest"] = metricas_rf
        self.modelos_info["random_forest"] = {
            "tipo": "random_forest",
            "metricas": metricas_rf
        }

        # 3. Gradient Boosting (similar a XGBoost lite)
        print("Entrenando Gradient Boosting...")
        gb = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
        gb.fit(X_scaled, y)
        self.modelos["gradient_boosting"] = gb

        metricas_gb = self._evaluar_modelo(gb, X_scaled, y, "Gradient Boosting")
        resultados["gradient_boosting"] = metricas_gb
        self.modelos_info["gradient_boosting"] = {
            "tipo": "gradient_boosting",
            "metricas": metricas_gb
        }

        self.entrenado = True

        # Guardar modelos
        self._guardar_modelos()

        return resultados

    def _evaluar_modelo(self, modelo, X, y, nombre: str) -> MetricasModelo:
        """Evaluar un modelo con métricas y validación cruzada."""
        y_pred = modelo.predict(X)

        mae = mean_absolute_error(y, y_pred)
        mse = mean_squared_error(y, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y, y_pred)

        # Validación cruzada 5-fold
        cv = KFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(modelo, X, y, cv=cv, scoring='neg_mean_absolute_error')
        cv_scores = -cv_scores  # Negativo porque scoring es 'neg_mean_absolute_error'

        print(f"  {nombre}: MAE={mae:.2f}, RMSE={rmse:.2f}, R²={r2:.3f}, CV MAE={cv_scores.mean():.2f}±{cv_scores.std():.2f}")

        return MetricasModelo(
            mae=round(mae, 4),
            mse=round(mse, 4),
            rmse=round(rmse, 4),
            r2=round(r2, 4),
            cv_scores=cv_scores.tolist(),
            cv_mean=round(cv_scores.mean(), 4),
            cv_std=round(cv_scores.std(), 4)
        )

    def predecir(self, distancia_km: float, trafico: str, hora: int,
                 dia: str = "Lunes", modelo: str = "mejor") -> Dict[str, Any]:
        """Predecir tiempo usando el modelo especificado o el mejor."""
        if not self.entrenado:
            raise ValueError("El modelo debe ser entrenado primero")

        if modelo == "mejor":
            # Usar el modelo con mejor R²
            mejor_r2 = -1
            mejor_modelo = "regresion_lineal"
            for nombre, info in self.modelos_info.items():
                if info["metricas"].r2 > mejor_r2:
                    mejor_r2 = info["metricas"].r2
                    mejor_modelo = nombre
            modelo = mejor_modelo

        if modelo not in self.modelos:
            raise ValueError(f"Modelo '{modelo}' no disponible")

        # Preparar features
        trafico_cod = self._codificar_trafico(trafico)
        dia_cod = self._codificar_dia(dia)
        X_nuevo = np.array([[distancia_km, trafico_cod, hora, dia_cod]])
        X_scaled = self.scaler.transform(X_nuevo)

        # Predicción
        tiempo = self.modelos[modelo].predict(X_scaled)[0]
        tiempo = max(0, tiempo)  # No negativo

        # Confianza basada en R²
        r2 = self.modelos_info[modelo]["metricas"].r2
        if r2 >= 0.85:
            confianza = "Alta"
        elif r2 >= 0.70:
            confianza = "Media"
        else:
            confianza = "Baja"

        return {
            "distancia": distancia_km,
            "nivel_trafico": trafico,
            "hora": hora,
            "tiempo_predicho": round(tiempo, 2),
            "confianza": confianza,
            "modelo_usado": modelo,
            "r2_score": r2,
            "mae": self.modelos_info[modelo]["metricas"].mae
        }

    def _guardar_modelos(self):
        """Guardar modelos entrenados en disco."""
        if not HAS_SKLEARN:
            return

        os.makedirs("backend/models", exist_ok=True)

        for nombre, modelo in self.modelos.items():
            joblib.dump(modelo, f"backend/models/{nombre}.pkl")

        joblib.dump(self.scaler, "backend/models/scaler.pkl")

        print(f"\nModelos guardados en backend/models/")

    def cargar_modelos(self) -> bool:
        """Cargar modelos guardados desde disco."""
        if not HAS_SKLEARN:
            return False

        try:
            self.modelos = {}
            for nombre in ["regresion_lineal", "random_forest", "gradient_boosting"]:
                path = f"backend/models/{nombre}.pkl"
                if os.path.exists(path):
                    self.modelos[nombre] = joblib.load(path)

            scaler_path = "backend/models/scaler.pkl"
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)

            if self.modelos:
                self.entrenado = True
                print(f"Modelos cargados: {list(self.modelos.keys())}")
                return True
        except Exception as e:
            print(f"Error al cargar modelos: {e}")

        return False

    def obtener_comparacion(self, distancia_km: float, trafico: str, hora: int) -> Dict[str, Any]:
        """Obtener predicciones de todos los modelos para comparar."""
        if not self.entrenado:
            raise ValueError("El modelo debe ser entrenado primero")

        resultados = {}

        for nombre in self.modelos.keys():
            result = self.predecir(distancia_km, trafico, hora, modelo=nombre)
            resultados[nombre] = {
                "tiempo_predicho": result["tiempo_predicho"],
                "confianza": result["confianza"],
                "r2_score": result["r2_score"]
            }

        return resultados

    def obtener_metricas_modelos(self) -> Dict[str, Dict]:
        """Obtener métricas de todos los modelos."""
        if not self.entrenado:
            return {}

        metricas = {}
        for nombre, info in self.modelos_info.items():
            m = info["metricas"]
            metricas[nombre] = {
                "mae": m.mae,
                "rmse": m.rmse,
                "r2": m.r2,
                "cv_mean": m.cv_mean,
                "cv_std": m.cv_std
            }

        return metricas


def entrenar_y_guardar():
    """Función standalone para entrenar y guardar modelos."""
    predictor = ModeloPredictor()

    # Intentar cargar modelos existentes
    if predictor.cargar_modelos():
        print("Modelos ya existen. No se re-entrena.")
        return predictor

    # Entrenar nuevos
    resultados = predictor.entrenar()

    print("\n=== Resumen de Modelos ===")
    for nombre, metricas in resultados.items():
        print(f"\n{nombre.upper()}:")
        print(f"  MAE: {metricas.mae:.2f} min")
        print(f"  RMSE: {metricas.rmse:.2f} min")
        print(f"  R²: {metricas.r2:.4f}")

    return predictor


if __name__ == "__main__":
    predictor = entrenar_y_guardar()

    # Prueba de predicción
    if predictor.entrenado:
        print("\n=== Prueba de Predicción ===")
        print("Distancia: 5km, Tráfico: Medio, Hora: 8")

        resultado = predictor.predecir(5.0, "Medio", 8)
        print(f"Tiempo predicho: {resultado['tiempo_predicho']} min")
        print(f"Confianza: {resultado['confianza']}")
        print(f"Modelo usado: {resultado['modelo_usado']}")