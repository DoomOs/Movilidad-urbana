import { useState, useEffect, lazy, Suspense } from 'react';
import { ThemeProvider, useTheme } from './hooks/useTheme';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './components/ui/card';
import { Button } from './components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Badge } from './components/ui/badge';
import { Switch } from './components/ui/switch';
import { Sun, Moon, MapPin, Navigation, BarChart3, Car, Bike, AlertTriangle, Clock, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import {
  obtenerCiudades, obtenerCalles, buscarRuta, predecirTiempo,
  compararModelos, obtenerAnalisis, obtenerMetricasML
} from './api';
import { StatsCards, TrafficChart, TimeDistributionChart, StreetsByCityChart, MLMetricsChart } from './components/Dashboard';

const MapComponent = lazy(() => import('./components/Map'));

const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
const CLIMAS = ['Despejado', 'Nublado', 'Lluvia Ligera', 'Lluvia Intensa'];
const VEHICULOS = [
  { value: 'automovil', label: 'Automóvil' },
  { value: 'bicicleta', label: 'Bicicleta' },
  { value: 'motocicleta', label: 'Motocicleta' },
];

function formatMin(min) {
  if (min < 60) return `${Math.round(min)} min`;
  const h = Math.floor(min / 60);
  const m = Math.round(min % 60);
  return `${h}h ${m}m`;
}

function AppContent() {
  const { theme, toggleTheme } = useTheme();
  const [tab, setTab] = useState('buscar');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [ciudades, setCiudades] = useState([]);
  const [calles, setCalles] = useState([]);
  const [analisis, setAnalisis] = useState(null);
  const [metricas, setMetricas] = useState(null);

  const [ciudad, setCiudad] = useState('');
  const [origen, setOrigen] = useState('');
  const [destino, setDestino] = useState('');
  const [hora, setHora] = useState(12);
  const [dia, setDia] = useState('Lunes');
  const [vehiculo, setVehiculo] = useState('automovil');
  const [clima, setClima] = useState('Despejado');

  const [resultados, setResultados] = useState([]);
  const [prediccion, setPrediccion] = useState(null);
  const [comparacionML, setComparacionML] = useState(null);

  const [mapCenter, setMapCenter] = useState([14.6349, -90.5069]);
  const [algoSeleccionado, setAlgoSeleccionado] = useState(null);

  // Cargar datos iniciales
  useEffect(() => {
    async function init() {
      try {
        const [cities, data, m] = await Promise.all([
          obtenerCiudades(),
          obtenerAnalisis(),
          obtenerMetricasML().catch(() => null)
        ]);
        setCiudades(cities);
        setAnalisis(data);
        setMetricas(m);
        if (cities.length > 0) setCiudad(cities[0].nombre);
      } catch (err) {
        console.error('Error init:', err);
      }
    }
    init();
  }, []);

  // Cargar calles al cambiar ciudad
  useEffect(() => {
    if (!ciudad) return;
    obtenerCalles(ciudad).then(data => {
      setCalles(data.calles || []);
      if (data.calles?.length >= 2) {
        setOrigen(data.calles[0]);
        setDestino(data.calles[1]);
      }
      // Actualizar centro del mapa
      const cityData = ciudades.find(c => c.nombre === ciudad);
      if (cityData?.latitud) setMapCenter([cityData.latitud, cityData.longitud]);
    }).catch(console.error);
  }, [ciudad, ciudades]);

  const handleBuscar = async () => {
    if (!origen || !destino || origen === destino) {
      setError('Selecciona origen y destino diferentes');
      return;
    }
    setLoading(true);
    setError(null);
    setResultados([]);
    setPrediccion(null);

    try {
      const data = { origen, destino, ciudad, hora, dia_semana: dia, tipo_vehiculo: vehiculo, clima };
      const results = await buscarRuta(data);
      setResultados(results);

      // Centrar mapa en primera coordenada disponible
      const firstCoords = results[0]?.coordenadas_ruta;
      if (firstCoords?.length > 0) {
        setMapCenter([firstCoords[0].lat, firstCoords[0].lng]);
      }
    } catch (err) {
      setError(err?.response?.data?.detail || 'Error al buscar ruta');
    } finally {
      setLoading(false);
    }
  };

  const handlePredecir = async () => {
    if (!resultados.length) return;
    setLoading(true);
    try {
      const dist = resultados[0]?.distancia_total || 5;
      const [pred, comp] = await Promise.all([
        predecirTiempo(dist, 'Medio', hora),
        compararModelos(dist, 'Medio', hora)
      ]);
      setPrediccion(pred);
      setComparacionML(comp.predicciones);
    } catch (err) {
      console.error('Error predicción:', err);
    } finally {
      setLoading(false);
    }
  };

  const mejor = resultados.length ? resultados.reduce((a, b) => a.tiempo_total < b.tiempo_total ? a : b) : null;

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
        <div className="container flex h-14 items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <div className="bg-primary p-1.5 rounded-lg">
              <Navigation className="h-4 w-4 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-base font-bold">Movilidad Guatemala</h1>
              <p className="text-[10px] text-muted-foreground">Sistema de Rutas con IA</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-muted-foreground hidden sm:inline">Modo</span>
            <Sun className="h-3 w-3" />
            <Switch checked={theme === 'dark'} onCheckedChange={toggleTheme} />
            <Moon className="h-3 w-3" />
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="container px-4 py-4 space-y-4">
        {/* Error alert */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-lg flex items-center gap-2 text-sm"
            >
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
              <button onClick={() => setError(null)} className="ml-auto hover:opacity-70">✕</button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Tabs */}
        <Tabs value={tab} onValueChange={setTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="buscar" className="gap-1.5 text-xs">
              <Navigation className="h-3 w-3" />
              Buscar Ruta
            </TabsTrigger>
            <TabsTrigger value="analisis" className="gap-1.5 text-xs">
              <BarChart3 className="h-3 w-3" />
              Análisis
            </TabsTrigger>
          </TabsList>

          {/* Tab: Buscar */}
          <TabsContent value="buscar" className="space-y-4">
            <div className="grid lg:grid-cols-2 gap-4">
              {/* Formulario */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Parámetros del Viaje</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Ciudad */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-muted-foreground">Ciudad</label>
                    <Select value={ciudad} onValueChange={setCiudad}>
                      <SelectTrigger className="h-9">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {ciudades.map(c => (
                          <SelectItem key={c.id} value={c.nombre}>{c.nombre}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Origen y Destino */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-muted-foreground">Origen</label>
                      <Select value={origen} onValueChange={setOrigen}>
                        <SelectTrigger className="h-9">
                          <SelectValue placeholder="Origen" />
                        </SelectTrigger>
                        <SelectContent>
                          {calles.map(c => (
                            <SelectItem key={c} value={c}>{c}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-muted-foreground">Destino</label>
                      <Select value={destino} onValueChange={setDestino}>
                        <SelectTrigger className="h-9">
                          <SelectValue placeholder="Destino" />
                        </SelectTrigger>
                        <SelectContent>
                          {calles.map(c => (
                            <SelectItem key={c} value={c}>{c}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {/* Hora */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-muted-foreground">
                      Hora: <span className="text-primary font-bold">{hora}:00</span>
                    </label>
                    <input type="range" min="0" max="23" value={hora} onChange={e => setHora(+e.target.value)} className="w-full" />
                    <div className="flex justify-between text-[10px] text-muted-foreground">
                      <span>0h</span><span>6h</span><span>12h</span><span>18h</span><span>23h</span>
                    </div>
                  </div>

                  {/* Día y Vehículo */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-muted-foreground">Día</label>
                      <Select value={dia} onValueChange={setDia}>
                        <SelectTrigger className="h-9">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {DIAS.map(d => <SelectItem key={d} value={d}>{d}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-muted-foreground">Vehículo</label>
                      <Select value={vehiculo} onValueChange={setVehiculo}>
                        <SelectTrigger className="h-9">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {VEHICULOS.map(v => <SelectItem key={v.value} value={v.value}>{v.label}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {/* Clima */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-muted-foreground">Clima</label>
                    <Select value={clima} onValueChange={setClima}>
                      <SelectTrigger className="h-9">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {CLIMAS.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>

                  <Button onClick={handleBuscar} disabled={loading} className="w-full" size="sm">
                    {loading ? 'Buscando...' : 'Buscar Ruta'}
                  </Button>
                </CardContent>
              </Card>

              {/* Mapa */}
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">Mapa</CardTitle>
                    {resultados.length > 0 && (
                      <div className="flex gap-1">
                        {resultados.map(r => (
                          <button
                            key={r.algoritmo}
                            onClick={() => setAlgoSeleccionado(algoSeleccionado === r.algoritmo ? null : r.algoritmo)}
                            className={`px-2 py-0.5 rounded text-[10px] font-medium transition ${
                              algoSeleccionado === r.algoritmo ? 'ring-2 ring-primary' : 'opacity-70 hover:opacity-100'
                            }`}
                            style={{
                              backgroundColor: r.algoritmo === 'A*' ? '#22c55e' : r.algoritmo === 'BFS' ? '#3b82f6' : '#a855f7',
                              color: 'white'
                            }}
                          >
                            {r.algoritmo}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="h-[300px] rounded-md overflow-hidden border">
                    <Suspense fallback={<div className="h-full flex items-center justify-center text-muted-foreground text-sm">Cargando mapa...</div>}>
                      <MapComponent
                        center={mapCenter}
                        zoom={13}
                        resultados={resultados}
                        selectedAlgorithm={algoSeleccionado}
                      />
                    </Suspense>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Resultados */}
            {resultados.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-muted-foreground">Resultados de Búsqueda</h3>
                <div className="grid sm:grid-cols-3 gap-3">
                  {resultados.map((r) => {
                    const isBest = r.algoritmo === mejor?.algoritmo;
                    return (
                      <Card key={r.algoritmo} className={`relative ${isBest ? 'ring-2 ring-primary' : ''}`}>
                        {isBest && (
                          <Badge variant="success" className="absolute -top-2 -right-2 text-[10px]">Mejor</Badge>
                        )}
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm flex items-center gap-2">
                            <span
                              className="w-3 h-3 rounded-full"
                              style={{ backgroundColor: r.algoritmo === 'A*' ? '#22c55e' : r.algoritmo === 'BFS' ? '#3b82f6' : '#a855f7' }}
                            />
                            {r.algoritmo}
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-2 text-sm">
                          <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                            <span className="text-muted-foreground text-xs">Distancia:</span>
                            <span className="font-medium text-xs">{r.distancia_total} km</span>
                            <span className="text-muted-foreground text-xs">Tiempo:</span>
                            <span className="font-medium text-xs">{formatMin(r.tiempo_total)}</span>
                            {r.tiempo_ajustado && (
                              <>
                                <span className="text-muted-foreground text-xs">Ajustado:</span>
                                <span className="font-medium text-xs text-primary">{formatMin(r.tiempo_ajustado)}</span>
                              </>
                            )}
                            <span className="text-muted-foreground text-xs">Nodos:</span>
                            <span className="font-medium text-xs">{r.nodos_expandidos}</span>
                          </div>

                          {/* Ruta */}
                          <div className="pt-2 border-t">
                            <p className="text-[10px] text-muted-foreground mb-1">Ruta:</p>
                            <p className="text-[11px] leading-tight truncate font-mono">
                              {r.ruta.join(' → ')}
                            </p>
                          </div>

                          {/* Recomendaciones */}
                          {r.recomendaciones?.length > 0 && (
                            <div className="flex flex-wrap gap-1 pt-1">
                              {r.recomendaciones.map((rec, i) => (
                                <Badge key={i} variant="outline" className="text-[10px]">{rec}</Badge>
                              ))}
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>

                {/* Predicción ML */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Predicción con Machine Learning</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button onClick={handlePredecir} disabled={loading} variant="secondary" size="sm">
                      {loading ? 'Procesando...' : 'Predecir Tiempo'}
                    </Button>

                    {prediccion && (
                      <div className="grid sm:grid-cols-2 gap-4">
                        <div className="p-3 bg-muted rounded-lg">
                          <p className="text-[10px] text-muted-foreground mb-1">Tiempo Predicho</p>
                          <p className="text-2xl font-bold">{prediccion.tiempo_predicho} <span className="text-sm font-normal">min</span></p>
                          <div className="flex gap-2 mt-2">
                            <Badge variant={prediccion.confianza === 'Alta' ? 'success' : prediccion.confianza === 'Media' ? 'info' : 'warning'} className="text-[10px]">
                              {prediccion.confianza}
                            </Badge>
                            <Badge variant="outline" className="text-[10px]">{prediccion.modelo_usado}</Badge>
                          </div>
                        </div>

                        {comparacionML && (
                          <div className="space-y-1.5">
                            <p className="text-xs font-medium text-muted-foreground">Modelos</p>
                            {Object.entries(comparacionML).map(([modelo, datos]) => (
                              <div key={modelo} className="flex justify-between items-center text-xs">
                                <span className="capitalize">{modelo.replace('_', ' ')}</span>
                                <Badge variant="outline" className="text-[10px]">{datos.tiempo_predicho?.toFixed(1)} min</Badge>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          {/* Tab: Análisis */}
          <TabsContent value="analisis" className="space-y-4">
            <StatsCards stats={analisis} />
            <div className="grid md:grid-cols-2 gap-4">
              <TrafficChart data={analisis?.estadisticas_trafico} />
              <TimeDistributionChart stats={analisis?.estadisticas_tiempo} />
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <StreetsByCityChart data={analisis?.calles_por_ciudad} />
              <MLMetricsChart metricas={metricas?.modelos} />
            </div>
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t py-4 mt-8">
        <div className="container text-center text-xs text-muted-foreground">
          Sistema de Movilidad Urbana Guatemala • IA para optimización de rutas
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}