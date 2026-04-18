# Sistema Inteligente de Recomendación y Toma de Decisiones para Movilidad Urbana

## Introducción al Software

Este proyecto implementa un sistema completo de Inteligencia Artificial para la recomendación de rutas urbanas óptimas. El sistema integra múltiples técnicas de IA incluyendo algoritmos de búsqueda, lógica de predicados y modelos de Machine Learning para proporcionar recomendaciones inteligentes de movilidad urbana.

### Características Principales

1. **Búsqueda de Rutas**: Implementación de tres algoritmos de búsqueda (BFS, DFS, A*) para encontrar rutas entre dos puntos
2. **Lógica de Predicados**: Sistema basado en reglas tipo Prolog con 7 reglas de decisión para ajustar recomendaciones
3. **Machine Learning**: Modelo de regresión lineal para predicción de tiempos de viaje
4. **Análisis de Datos**: Procesamiento y análisis exploratorio con Pandas
5. **Interfaz Interactiva**: Dashboard en React para visualización de resultados

### Componentes de IA Aplicados

| Unidad | Concepto | Aplicación en el Proyecto |
|--------|----------|---------------------------|
| Introducción a IA | Sistema inteligente | Recomendador de rutas urbano |
| Agentes | Agente inteligente | Agente recomendador con percepción de tráfico |
| Complejidad | Evaluación de algoritmos | Comparativa BFS vs DFS vs A* |
| Búsqueda | Algoritmos informados/no informados | BFS, DFS, A* con heurística euclidiana |
| Lógica de Predicados | Reglas de decisión | 7 reglas tipo "si-entonces" |
| Machine Learning | Regresión lineal | Predicción de tiempo de viaje |
| Robótica/Interacción | API + Frontend | Integración completa con React |

## Tecnologías Usadas

### Backend (Python)

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.8+ | Lenguaje principal |
| FastAPI | 0.100+ | Framework para API REST |
| Pandas | 2.0+ | Manipulación y análisis de datos |
| NumPy | 1.24+ | Cálculos numéricos |
| Uvicorn | 0.23+ | Servidor ASGI |

### Frontend (JavaScript/React)

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| React | 18.2+ | Framework de interfaz |
| Vite | 5.0+ | Build tool y dev server |
| Axios | 1.6+ | Cliente HTTP |
| CSS3 | - | Estilos y diseño responsive |

### Herramientas de Desarrollo

| Herramienta | Propósito |
|-------------|-----------|
| Git | Control de versiones |
| npm | Gestor de paquetes Node.js |
| pip | Gestor de paquetes Python |

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)                  │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  Formulario │  │ Visualización│  │  Comparación    │   │
│  │  de Búsqueda│  │  de Rutas    │  │  de Algoritmos  │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/JSON
┌─────────────────────────────────────────────────────────────┐
│                      API REST (FastAPI)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ /buscar  │  │/comparar │  │/predecir │  │ /analisis│   │
│  │  -ruta   │  │-algoritmo│  │ -tiempo  │  │  -datos  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   MOTOR DE IA (Python)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  Buscador    │  │  Lógica de   │  │  Modelo de ML   │  │
│  │  de Rutas    │  │  Predicados  │  │  (Regresión)    │  │
│  │  BFS/DFS/A*  │  │  7 Reglas    │  │  Predicción     │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Pandas - Análisis y Procesamiento           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      DATASET (CSV)                          │
│  Columnas: origen, destino, ciudad, distancia_km, trafico, │
│            clima, hora, dia_semana, tiempo_estimado_min    │
│  150 registros simulados con calles reales de México       │
└─────────────────────────────────────────────────────────────┘
```

## Estructura de Archivos del Proyecto

```
/workspace/
│
├── backend/                        # Módulo principal de IA
│   ├── generador_dataset.py        # Generación de dataset realista
│   │   └── Clase: GeneradorDatasetTrafico
│   │       - 10 ciudades mexicanas
│   │       - Calles reales por ciudad
│   │       - Simulación de tráfico, clima, horas
│   │
│   ├── buscador_rutas.py           # Algoritmos de búsqueda
│   │   ├── Clase: GrafoTrafico
│   │   │   - Construcción de grafo desde DataFrame
│   │   │   - Coordenadas para heurística
│   │   ├── Clase: BuscadorRutas
│   │   │   - bfs(): Búsqueda en anchura
│   │   │   - dfs(): Búsqueda en profundidad
│   │   │   - a_estrella(): Búsqueda A* con heurística
│   │   └── Clase: ResultadoBusqueda
│   │
│   ├── logica_predicados.py        # Motor de reglas
│   │   ├── Clase: MotorInferencia
│   │   │   - Base de hechos
│   │   │   - Evaluación de condiciones
│   │   ├── Clase: SistemaReglasTrafico
│   │   │   - 7 reglas implementadas:
│   │   │     1. Evitar tráfico alto en larga distancia
│   │   │     2. Ajustar tiempo por lluvia
│   │   │     3. Evitar zonas escolares en hora pico
│   │   │     4. Bicicletas evitan autopistas
│   │   │     5. Priorizar distancia con combustible caro
│   │   │     6. Tráfico reducido fin de semana
│   │   │     7. Precaución nocturna
│   │   └── Clases: Hecho, Regla, TipoRegla
│   │
│   ├── modelo_ml.py                # Machine Learning
│   │   └── Clase: ModeloPrediccionTiempo
│   │       - Regresión lineal múltiple desde cero
│   │       - Método de ecuación normal
│   │       - Normalización de características
│   │       - Métricas: MAE, MSE, RMSE, R²
│   │       - Guardar/cargar modelo (pickle)
│   │
│   ├── api.py                      # API REST FastAPI
│   │   ├── Endpoints:
│   │   │   - GET  /                # Información API
│   │   │   - GET  /ciudades        # Lista de ciudades
│   │   │   - GET  /calles/{ciudad} # Calles por ciudad
│   │   │   - POST /buscar-ruta     # Buscar ruta (3 algoritmos)
│   │   │   - GET  /comparar-algoritmos # Comparar BFS/DFS/A*
│   │   │   - POST /predecir-tiempo # Predicción ML
│   │   │   - GET  /analisis-datos  # Estadísticas dataset
│   │   │   - GET  /salud           # Health check
│   │   └── Modelos Pydantic: SolicitudRuta, ResultadoRuta, etc.
│   │
│   └── modelo_prediccion.pkl       # Modelo ML pre-entrenado
│
├── frontend/                       # Interfaz React
│   ├── package.json                # Dependencias npm
│   ├── vite.config.js              # Configuración Vite
│   ├── index.html                  # HTML principal
│   └── src/
│       ├── main.jsx                # Punto de entrada React
│       ├── App.jsx                 # Componente principal
│       ├── api.js                  # Cliente API axios
│       └── index.css               # Estilos CSS
│
├── datasets/                       # Datos
│   └── trafico_urbano.csv          # Dataset generado (150 registros)
│
├── docs/                           # Documentación
│   └── (documentación técnica)
│
└── README.md                       # Este archivo
```

## Guía Detallada de Instalación en Windows

### Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

1. **Python 3.8 o superior**
2. **Node.js 18 o superior**
3. **Git** (opcional, para clonar el repositorio)

### Paso 1: Verificar Instalaciones

Abre PowerShell o Símbolo del sistema y ejecuta:

```bash
python --version
node --version
npm --version
```

Si alguno no está instalado, descarga e instala:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/

### Paso 2: Instalar Dependencias del Backend

```bash
# Navegar al directorio del proyecto
cd C:\ruta\a\tu\proyecto\workspace

# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Instalar dependencias de Python
pip install fastapi uvicorn pandas numpy pydantic
```

### Paso 3: Generar Dataset

```bash
# Ejecutar generador de dataset
python backend/generador_dataset.py
```

Esto creará el archivo `datasets/trafico_urbano.csv` con 150 registros.

### Paso 4: Entrenar Modelo de ML

```bash
# Entrenar y guardar modelo
python backend/modelo_ml.py
```

Se creará `backend/modelo_prediccion.pkl`.

### Paso 5: Iniciar Servidor Backend

```bash
# Desde el directorio backend
cd backend

# Iniciar servidor FastAPI
python api.py
```

El servidor se ejecutará en http://localhost:8000

Puedes verificar la documentación interactiva en: http://localhost:8000/docs

### Paso 6: Instalar Dependencias del Frontend

Abre una **nueva terminal** (mantén el backend corriendo):

```bash
# Navegar al frontend
cd C:\ruta\a\tu\proyecto\workspace\frontend

# Instalar dependencias de Node.js
npm install
```

### Paso 7: Iniciar Servidor de Desarrollo Frontend

```bash
# En la misma terminal del frontend
npm run dev
```

La aplicación se abrirá automáticamente en http://localhost:3000

### Paso 8: Verificar Funcionamiento

1. **Backend**: Abre http://localhost:8000/salud
   - Deberías ver: `{"estado": "ok", "componentes": {...}}`

2. **Frontend**: Abre http://localhost:3000
   - Deberías ver la interfaz con el formulario de búsqueda

3. **Documentación API**: Abre http://localhost:8000/docs
   - Prueba los endpoints interactivamente

## Uso de la Aplicación

### Buscar Ruta

1. Selecciona una ciudad del dropdown
2. Elige calle de origen y destino
3. Configura hora, día, vehículo y clima
4. Haz clic en "Buscar Ruta Óptima"
5. Compara resultados de BFS, DFS y A*

### Ver Análisis de Datos

1. Haz clic en la pestaña "Análisis de Datos"
2. Explora estadísticas del dataset
3. Revisa distribución de tráfico y tiempos

### Predicción con ML

1. Después de buscar una ruta
2. Haz clic en "Predecir Tiempo con ML"
3. Observa la predicción del modelo

## Explicación de la IA Aplicada

### 1. Agente Inteligente

El sistema modela un agente recomendador de rutas con:
- **Estado**: Ubicación actual (calle)
- **Acciones**: Moverse entre nodos conectados
- **Percepción**: Nivel de tráfico, clima, hora
- **Objetivo**: Minimizar tiempo de viaje

### 2. Algoritmos de Búsqueda

#### BFS (Búsqueda No Informada)
- Explora nivel por nivel
- Garantiza camino más corto en número de nodos
- Complejidad: O(b^d)

#### DFS (Búsqueda No Informada)
- Explora en profundidad primero
- Menor uso de memoria
- No garantiza optimalidad

#### A* (Búsqueda Informada)
- Usa heurística h(n) = distancia euclidiana al destino
- Combina costo real g(n) + heurística h(n)
- Garantiza optimalidad con heurística admisible
- Más eficiente que BFS/DFS

### 3. Lógica de Predicados

Sistema basado en reglas con motor de inferencia:

```python
# Ejemplo de regla
SI trafico == "Alto" Y distancia > 5km
ENTONCES descartar_ruta = True
       factor_tiempo = 2.0
```

**7 Reglas Implementadas:**
1. Tráfico alto + distancia larga → Descartar
2. Lluvia → Ajustar tiempo (1.2x - 1.5x)
3. Hora pico → Evitar zonas escolares
4. Bicicleta → Evitar autopistas
5. Combustible caro → Priorizar distancia
6. Fin de semana → Tiempo optimista (0.85x)
7. Noche → Ruta iluminada preferida

### 4. Machine Learning

**Modelo**: Regresión Lineal Múltiple

**Características**:
- distancia_km (continua)
- trafico_codificado (ordinal: 1-4)
- hora (continua: 0-23)

**Variable Objetivo**: tiempo_estimado_min

**Ecuación**:
```
tiempo = β₀ + β₁·distancia + β₂·tráfico + β₃·hora
```

**Métricas de Evaluación**:
- MAE: Error absoluto medio (~4 minutos)
- R²: Coeficiente de determinación (~0.75)

### 5. Análisis con Pandas

Operaciones realizadas:
- Limpieza de datos
- Análisis exploratorio (EDA)
- Transformaciones (codificación categóricas)
- Estadísticas descriptivas
- Agrupaciones y agregaciones

## Comparación de Enfoques

| Algoritmo | Ventaja | Desventaja | Mejor Caso de Uso |
|-----------|---------|------------|-------------------|
| BFS | Óptimo en nodos | Memory-intensive | Grafos pequeños |
| DFS | Bajo consumo memoria | No óptimo | Exploración rápida |
| A* | Óptimo + eficiente | Requiere heurística | Producción |

## Solución de Problemas Comunes

### Error: "Module not found" en Backend

```bash
# Reinstalar dependencias
pip install --upgrade pip
pip install fastapi uvicorn pandas numpy pydantic
```

### Error: "npm install fails" en Frontend

```bash
# Limpiar caché de npm
npm cache clean --force

# Eliminar node_modules y reinstalar
rmdir /s /q node_modules
del package-lock.json
npm install
```

### Error: CORS en Frontend

Verifica que el backend esté corriendo en puerto 8000 y el frontend en 3000.

### Error: Puerto ya en uso

```bash
# Windows - Matar proceso en puerto 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## Entregables del Proyecto

1. ✅ Código fuente completo (backend + frontend)
2. ✅ Dataset (datasets/trafico_urbano.csv)
3. ✅ Documento técnico (este README)
4. ⏳ Video demostrativo (por generar)

## Posibles Extensiones Futuras

- Integración con Google Maps API
- Redes neuronales profundas
- Simulación en tiempo real
- Sistemas multi-agente
- Base de datos PostgreSQL
- Autenticación de usuarios
- Historial de búsquedas

## Autor

Proyecto desarrollado como parte del curso de Inteligencia Artificial.

## Licencia

Uso educativo y académico.
