import { useState, useEffect, Suspense, lazy } from 'react';
import { ThemeProvider, useTheme } from './hooks/useTheme';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Badge } from './components/ui/badge';
import { Switch } from './components/ui/switch';
import { Card as UICard } from './components/ui/card';
import { Sun, Moon, MapPin, Search, BarChart3, Car, Bike, AlertTriangle, Clock, CheckCircle2, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { formatTime, formatDistance, getTrafficColor } from './lib/utils';

import {
  obtenerCiudades, obtenerCalles, buscarRuta, predecirTiempo,
  compararModelos, obtenerAnalisis, obtenerMetricasML, verificarSalud
} from './api';
import {
  StatsCards, TrafficChart, TimeDistributionChart,
  StreetsByCityChart, MLMetricsChart, RecentRecordsTable
} from './components/Dashboard';

// Lazy load Map component
const MapComponent = lazy(() => import('./components/Map'));

const DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
const CLIMAS = ['Despejado', 'Nublado', 'Lluvia Ligera', 'Lluvia Intensa'];
const VEHICULOS = [
  { value: 'automovil', label: 'Automóvil', icon: Car },
  { value: 'bicicleta', label: 'Bicicleta', icon: Bike },
  { value: 'motocicleta', label: 'Motocicleta', icon: Bike },
];

function AppContent() {
  const { theme, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState('buscar');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Data states
  const [ciudades, setCiudades] = useState([]);
  const [calles, setCalles] = useState([]);
  const [analisis, setAnalisis] = useState(null);
  const [metricasML, setMetricasML] = useState(null);

  // Form states
  const [ciudadSeleccionada, setCiudadSeleccionada] = useState('');
  const [origen, setOrigen] = useState('');
  const [destino, setDestino] = useState('');
  const [hora, setHora] = useState(12);
  const [diaSemana, setDiaSemana] = useState('Lunes');
  const [vehiculo, setVehiculo] = useState('automovil');
  const [clima, setClima] = useState('Despejado');

  // Results states
  const [resultados, setResultados] = useState([]);
  const [comparacion, setComparacion] = useState(null);
  const [prediccion, setPrediccion] = useState(null);
  const [comparacionML, setComparacionML] = useState(null);

  // Map center
  const [mapCenter, setMapCenter] = useState([14.6349, -90.5069]);
  const [selectedAlgo, setSelectedAlgo] = useState(null);

  // Load initial data
  useEffect(() => {
    const init = async () => {
      try {
        const health = await verificarSalud();
        const cities = await obtenerCiudades();
        const data = await obtenerAnalisis();
        const metricas = await obtenerMetricasML();

        setCiudades(cities);
        setAnalisis(data);
        setMetricasML(metricas);

        if (cities.length > 0) {
          setCiudadSeleccionada(cities[0].nombre);
        }
      } catch (err) {
        console.error('Error initializing:', err);
      }
    };
    init();
  }, []);

  // Load streets when city changes
  useEffect(() => {
    if (ciudadSeleccionada) {
      const cityData = ciudades.find(c => c.nombre === ciudadSeleccionada);
      if (cityData && cityData.latitud && cityData.longitud) {
        setMapCenter([cityData.latitud, cityData.longitud]);
      }

      obtenerCalles(ciudadSeleccionada).then(data => {
        setCalles(data.calles || []);
        if (data.calles && data.calles.length >= 2) {
          setOrigen(data.calles[0]);
          setDestino(data.calles[1]);
        }
      }).catch(console.error);
    }
  }, [ciudadSeleccionada, ciudades]);

  const handleBuscar = async () => {
    if (!origen || !destino) {
      setError('Selecciona origen y destino');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const datos = {
        origen,
        destino,
        ciudad: ciudadSeleccionada,
        hora,
        dia_semana: diaSemana,
        tipo_vehiculo: vehiculo,
        clima,
      };

      const results = await buscarRuta(datos);
      setResultados(results);

      if (results.length > 0 && results[0].coordenadas_ruta && results[0].coordenadas_ruta.length > 0) {
        const firstCoord = results[0].coordenadas_ruta[0];
        setMapCenter([firstCoord.lat, firstCoord.lng]);
      }

      setSuccess('Rutas encontradas');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al buscar ruta');
    } finally {
      setLoading(false);
    }
  };

  const handlePredecir = async () => {
    if (resultados.length === 0) {
      setError('Primero busca una ruta');
      return;
    }

    setLoading(true);

    try {
      const distancia = resultados[0]?.distancia_total || 5;
      const result = await predecirTiempo(distancia, 'Medio', hora);
      setPrediccion(result);

      const compML = await compararModelos(distancia, 'Medio', hora);
      setComparacionML(compML.predicciones);
    } catch (err) {
      setError('Error al predecir');
    } finally {
      setLoading(false);
    }
  };

  const mejorResultado = resultados.length > 0
    ? resultados.reduce((a, b) => a.tiempo_total < b.tiempo_total ? a : b)
    : null;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <div className="bg-primary p-2 rounded-lg">
              <MapPin className="h-5 w-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-lg font-bold">Sistema de Movilidad GT</h1>
              <p className="text-xs text-muted-foreground">IA para rutas en Guatemala</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Sun className="h-4 w-4" />
              <Switch checked={theme === 'dark'} onCheckedChange={toggleTheme} />
              <Moon className="h-4 w-4" />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container px-4 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="buscar" className="gap-2">
              <Search className="h-4 w-4" />
              Buscar Ruta
            </TabsTrigger>
            <TabsTrigger value="analisis" className="gap-2">
              <BarChart3 className="h-4 w-4" />
              Análisis de Datos
            </TabsTrigger>
          </TabsList>

          {/* Tab: Buscar Ruta */}
          <TabsContent value="buscar" className="space-y-6">
            {/* Alerts */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="bg-destructive/10 text-destructive p-4 rounded-lg flex items-center gap-2"
                >
                  <AlertTriangle className="h-5 w-5" />
                  {error}
                  <Button variant="ghost" size="icon" onClick={() => setError(null)} className="ml-auto">
                    <X className="h-4 w-4" />
                  </Button>
                </motion.div>
              )}
              {success && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="bg-green-500/10 text-green-600 p-4 rounded-lg flex items-center gap-2"
                >
                  <CheckCircle2 className="h-5 w-5" />
                  {success}
                </motion.div>
              )}
            </AnimatePresence>

            <div className="grid lg:grid-cols-2 gap-6">
              {/* Form */}
              <Card>
                <CardHeader>
                  <CardTitle>Parámetros del Viaje</CardTitle>
                  <CardDescription>Ingresa los datos para buscar la mejor ruta</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Ciudad */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Ciudad</label>
                    <Select value={ciudadSeleccionada} onValueChange={setCiudadSeleccionada}>
                      <SelectTrigger>
                        <SelectValue placeholder="Seleccionar ciudad" />
                      </SelectTrigger>
                      <SelectContent>
                        {ciudades.map(c => (
                          <SelectItem key={c.id} value={c.nombre}>{c.nombre}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Origen y Destino */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Origen</label>
                      <Select value={origen} onValueChange={setOrigen}>
                        <SelectTrigger>
                          <SelectValue placeholder="Origen" />
                        </SelectTrigger>
                        <SelectContent>
                          {calles.map(c => (
                            <SelectItem key={c} value={c}>{c}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Destino</label>
                      <Select value={destino} onValueChange={setDestino}>
                        <SelectTrigger>
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
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Hora del día: {hora}:00</label>
                    <input
                      type="range"
                      min="0"
                      max="23"
                      value={hora}
                      onChange={e => setHora(parseInt(e.target.value))}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>0:00</span>
                      <span>12:00</span>
                      <span>23:00</span>
                    </div>
                  </div>

                  {/* Día y Vehículo */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Día</label>
                      <Select value={diaSemana} onValueChange={setDiaSemana}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {DIAS_SEMANA.map(d => (
                            <SelectItem key={d} value={d}>{d}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Vehículo</label>
                      <Select value={vehiculo} onValueChange={setVehiculo}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {VEHICULOS.map(v => (
                            <SelectItem key={v.value} value={v.value}>{v.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {/* Clima */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Clima</label>
                    <Select value={clima} onValueChange={setClima}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {CLIMAS.map(c => (
                          <SelectItem key={c} value={c}>{c}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <Button onClick={handleBuscar} disabled={loading} className="w-full" size="lg">
                    {loading ? 'Buscando...' : 'Buscar Ruta Óptima'}
                  </Button>
                </CardContent>
              </Card>

              {/* Map */}
              <Card>
                <CardHeader>
                  <CardTitle>Mapa de Rutas</CardTitle>
                  <CardDescription>
                    {resultados.length > 0
                      ? `Mostrando ${resultados.length} rutas encontradas`
                      : 'Selecciona origen y destino para ver las rutas'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[400px] rounded-lg overflow-hidden border">
                    <Suspense fallback={<div className="h-full flex items-center justify-center">Cargando mapa...</div>}>
                      <MapComponent
                        center={mapCenter}
                        zoom={13}
                        resultados={resultados}
                        selectedAlgorithm={selectedAlgo}
                      />
                    </Suspense>
                  </div>

                  {/* Legend */}
                  {resultados.length > 0 && (
                    <div className="flex gap-4 mt-4 justify-center">
                      {resultados.map(r => (
                        <Button
                          key={r.algoritmo}
                          variant={selectedAlgo === r.algoritmo ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => setSelectedAlgo(selectedAlgo === r.algoritmo ? null : r.algoritmo)}
                        >
                          <Badge
                            className="mr-2"
                            style={{ backgroundColor: r.algoritmo === 'A*' ? '#22c55e' : r.algoritmo === 'BFS' ? '#3b82f6' : '#a855f7' }}
                          >
                            {r.algoritmo}
                          </Badge>
                          {formatTime(r.tiempo_total)}
                        </Button>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Results */}
            {resultados.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="grid md:grid-cols-3 gap-4"
              >
                {resultados.map((resultado, idx) => {
                  const isBest = resultado.algoritmo === mejorResultado?.algoritmo;
                  return (
                    <UICard
                      key={idx}
                      className={`relative overflow-hidden ${isBest ? 'ring-2 ring-primary' : ''}`}
                    >
                      {isBest && (
                        <Badge className="absolute top-2 right-2" variant="success">
                          ✓ Mejor
                        </Badge>
                      )}
                      <CardHeader className="pb-2">
                        <CardTitle className="text-lg flex items-center gap-2">
                          <Badge
                            style={{
                              backgroundColor: resultado.algoritmo === 'A*' ? '#22c55e' : resultado.algoritmo === 'BFS' ? '#3b82f6' : '#a855f7'
                            }}
                          >
                            {resultado.algoritmo}
                          </Badge>
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div>
                            <span className="text-muted-foreground">Distancia:</span>
                            <span className="ml-1 font-medium">{formatDistance(resultado.distancia_total)}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Tiempo:</span>
                            <span className="ml-1 font-medium">{formatTime(resultado.tiempo_total)}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Ajustado:</span>
                            <span className="ml-1 font-medium">{formatTime(resultado.tiempo_ajustado || resultado.tiempo_total)}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Nodos:</span>
                            <span className="ml-1 font-medium">{resultado.nodos_expandidos}</span>
                          </div>
                        </div>

                        <div className="text-xs text-muted-foreground">
                          <span className="font-medium">Ruta:</span>
                          <div className="truncate">{resultado.ruta.join(' → ')}</div>
                        </div>

                        {resultado.advertencias?.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {resultado.advertencias.map((adv, i) => (
                              <Badge key={i} variant="warning" className="text-xs">
                                {adv}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </CardContent>
                    </UICard>
                  );
                })}
              </motion.div>
            )}

            {/* ML Prediction */}
            {resultados.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Predicción con Machine Learning</CardTitle>
                  <CardDescription>Compara diferentes modelos predictivos</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button onClick={handlePredecir} disabled={loading} variant="secondary">
                    {loading ? 'Prediciendo...' : 'Predecir con ML'}
                  </Button>

                  {prediccion && (
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="p-4 bg-muted rounded-lg">
                        <div className="text-sm text-muted-foreground">Tiempo Predicho</div>
                        <div className="text-3xl font-bold">{prediccion.tiempo_predicho} min</div>
                        <div className="flex gap-2 mt-2">
                          <Badge variant={prediccion.confianza === 'Alta' ? 'success' : prediccion.confianza === 'Media' ? 'info' : 'warning'}>
                            Confianza: {prediccion.confianza}
                          </Badge>
                          <Badge variant="outline">{prediccion.modelo_usado}</Badge>
                        </div>
                      </div>

                      {comparacionML && (
                        <div className="space-y-2">
                          <div className="text-sm font-medium">Comparación de Modelos</div>
                          {Object.entries(comparacionML).map(([modelo, datos]) => (
                            <div key={modelo} className="flex justify-between items-center text-sm">
                              <span className="capitalize">{modelo.replace('_', ' ')}</span>
                              <Badge variant="outline">{datos.tiempo_predicho?.toFixed(1)} min</Badge>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Tab: Análisis */}
          <TabsContent value="analisis" className="space-y-6">
            <StatsCards stats={analisis} />

            <div className="grid md:grid-cols-2 gap-6">
              <TrafficChart data={analisis?.estadisticas_trafico} />
              <TimeDistributionChart stats={analisis?.estadisticas_tiempo} />
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <StreetsByCityChart data={analisis?.calles_por_ciudad} />
              <MLMetricsChart metricas={metricasML?.modelos} />
            </div>

            <RecentRecordsTable registros={analisis?.registros_recientes} />
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t py-6 mt-12">
        <div className="container text-center text-sm text-muted-foreground">
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