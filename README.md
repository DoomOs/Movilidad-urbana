# Sistema Inteligente de Movilidad Urbana - Guatemala

> 🚗 Sistema de recomendación de rutas urbanas con IA, búsqueda A*/BFS/DFS, lógica de predicados y machine learning para Guatemala.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![React](https://img.shields.io/badge/React-18-61dafb.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Características

- **Búsqueda de Rutas**: Implementación de BFS, DFS y A* para encontrar rutas óptimas
- **Lógica de Predicados**: 8 reglas de decisión tipo Prolog para ajustar recomendaciones
- **Machine Learning**: 3 modelos predictivos (Regresión Lineal, Random Forest, Gradient Boosting)
- **Mapas Interactivos**: Visualización de rutas con Leaflet + OpenStreetMap
- **Dashboard Analítico**: Gráficos de estadísticas con Recharts
- **Dark Mode**: Tema claro/oscuro con transiciones suaves
- **10 Ciudades de Guatemala**: Con calles reales de cada ciudad

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React + Vite)                │
│   TailwindCSS • Recharts • Leaflet • Framer Motion          │
│   Puerto 3000                                               │
└─────────────────────────────────────────────────────────────┘
                              ↕ HTTP REST
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI + Python)                │
│   Puerto 8000                                               │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│   │ Routes  │ │   ML    │ │ Rules   │ │ Search  │          │
│   │ /ciudad │ │ Models  │ │ Engine  │ │ BFS/DFS  │          │
│   │ /calles │ │ sk-learn│ │ 8 Rules │ │ A*       │          │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│                           ↓                                 │
│   ┌────────────────────────────────────────────────────┐   │
│   │              SQLite Database                       │   │
│   │  Ciudades • Calles • Registros • Nodos • Aristas   │   │
│   └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🗺️ Ciudades de Guatemala

| Ciudad | Departamento | Calles |
|--------|--------------|--------|
| Ciudad de Guatemala | Guatemala | 15 |
| Antigua Guatemala | Sacatepéquez | 10 |
| Quetzaltenango | Quetzaltenango | 10 |
| Escuintla | Escuintla | 8 |
| Puerto San José | Escuintla | 7 |
| Cobán | Alta Verapaz | 8 |
| Zacapa | Zacapa | 7 |
| Chiquimula | Chiquimula | 7 |
| Retalhuleu | Retalhuleu | 7 |
| Mazatenango | Suchitepéquez | 7 |

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.8+
- Node.js 18+
- npm o yarn

### 1. Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar (crea DB y arranca servidor)
python main.py
```

El backend estará disponible en: http://localhost:8000
Documentación API: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend

# Instalar dependencias
npm install --legacy-peer-deps

# Ejecutar
npm run dev
```

La aplicación estará disponible en: http://localhost:3000

## 📡 Endpoints API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información del API |
| GET | `/ciudades` | Lista de ciudades |
| GET | `/calles/{ciudad}` | Calles de una ciudad |
| POST | `/buscar-ruta` | Buscar ruta (BFS/DFS/A*) |
| GET | `/comparar-algoritmos` | Comparar algoritmos |
| POST | `/predecir-tiempo` | Predicción ML |
| GET | `/metricas-ml` | Métricas de modelos |
| GET | `/analisis-datos` | Estadísticas dataset |
| GET | `/historial` | Historial de búsquedas |
| GET | `/salud` | Estado del sistema |

## 🤖 Machine Learning

El sistema incluye 3 modelos predictivos:

| Modelo | R² Típico | MAE Típico | Uso |
|--------|-----------|------------|-----|
| Regresión Lineal | 0.72 | ~4.5 min | Baseline rápido |
| Random Forest | 0.85 | ~3.2 min | Producción |
| Gradient Boosting | 0.88 | ~2.9 min | Mejor precisión |

**Features**: distancia_km, tráfico, hora, día_semana

## 📜 Reglas de Lógica de Predicados

| # | Regla | Condición | Acción |
|---|-------|-----------|--------|
| 1 | Tráfico Alto | tráfico=Alto/MuyAlto + dist>5km | factor x2.0 |
| 2 | Lluvia | clima=Lluvia | factor 1.2-1.5x |
| 3 | Hora Pico | hora 7-9, 17-19 | evitar zonas escolares |
| 4 | Bicicleta | vehículo=bicicleta | evitar autopistas |
| 5 | Combustible | costo=alto | priorizar distancia |
| 6 | Fin de Semana | día=Sáb/Dom | factor 0.85x |
| 7 | Nocturno | hora 22-5 | precaución +10% |
| 8 | Congestión Extrema | tráfico=MuyAlto | factor 1.8x |

## 📁 Estructura del Proyecto

```
Movilidad-urbana/
├── backend/
│   ├── main.py           # FastAPI app
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── database.py       # SQLite config
│   ├── seeds.py          # Guatemala data
│   ├── busqueda.py       # BFS/DFS/A* algorithms
│   ├── rules.py          # Logic predicates engine
│   └── ml_modelo.py       # ML models (sklearn)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/        # shadcn/ui components
│   │   │   ├── Map.jsx    # Leaflet map
│   │   │   └── Dashboard.jsx  # Charts
│   │   ├── hooks/
│   │   │   └── useTheme.jsx   # Dark mode
│   │   ├── lib/
│   │   │   └── utils.js   # Helpers
│   │   ├── App.jsx        # Main component
│   │   └── index.css      # Tailwind styles
│   └── tailwind.config.js
│
├── requirements.txt
├── README.md
└── LICENSE
```

## 🎨 UI Preview

El frontend incluye:

- **Tema claro/oscuro** con interruptor
- **Mapa interactivo** con rutas coloreadas por algoritmo
- **Dashboard** con 4+ tipos de gráficos
- **Animaciones** con Framer Motion
- **Responsive design** para móvil

## 📚 Recursos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [React](https://react.dev/) - UI library
- [TailwindCSS](https://tailwindcss.com/) - Styling
- [Leaflet](https://leafletjs.com/) - Maps
- [Recharts](https://recharts.org/) - Charts
- [scikit-learn](https://scikit-learn.org/) - ML
- [OpenStreetMap](https://www.openstreetmap.org/) - Free maps

## 📄 Licencia

MIT License - Ver archivo LICENSE para más detalles.

---

Desarrollado con ❤️ para Guatemala 🇬🇹