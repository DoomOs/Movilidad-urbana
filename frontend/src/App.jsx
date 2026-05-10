import { useState, useEffect, lazy, Suspense } from 'react';
import { ThemeProvider, useTheme } from './hooks/useTheme';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Badge } from './components/ui/badge';
import { Switch } from './components/ui/switch';
import { Sun, Moon, Navigation, BarChart3, AlertTriangle, Map } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import {
  obtenerCiudades, obtenerCalles, buscarRuta, predecirTiempo,
  compararModelos, obtenerAnalisis, obtenerMetricasML, obtenerGrafoCompleto
} from './api';
import { StatsCards, TrafficChart, TimeDistributionChart, StreetsByCityChart, MLMetricsChart } from './components/Dashboard';
import RouteNodes from './components/RouteNodes';
import GrafoVisual from './components/GrafoVisual';

const CityMap = lazy(() => import('./components/CityMap'));

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

export default function App() {
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
  const [algoSeleccionado, setAlgoSeleccionado] = useState(null);

  const [grafoCompleto, setGrafoCompleto] = useState(null);

  // Cargar datos iniciales
  useEffect(() => {
    async function init() {
      try {
        const [cities, data, m, grafo] = await Promise.all([
          obtenerCiudades(),
          obtenerAnalisis(),
          obtenerMetricasML().catch(() => null),
          obtenerGrafoCompleto().catch(() => null)
        ]);
        setCiudades(cities);
        setAnalisis(data);
        setMetricas(m);
        setGrafoCompleto(grafo);
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
    }).catch(console.error);
  }, [ciudad]);

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
      const data = {
        origen,
        destino,
        ciudad,
        hora,
        dia_semana: dia,
        tipo_vehiculo: vehiculo,
        clima
      };
      const results = await buscarRuta(data);
      setResultados(results);
      setAlgoSeleccionado(results[0]?.algoritmo);
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

  const mejor = resultados.length
    ? resultados.reduce((a, b) => a.tiempo_total < b.tiempo_total ? a : b)
    : null;

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
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="buscar" className="gap-1.5 text-xs">
              <Navigation className="h-3 w-3" />
              Buscar Ruta
            </TabsTrigger>
            <TabsTrigger value="mapa" className="gap-1.5 text-xs">
              <Map className="h-3 w-3" />
              Mapa
            </TabsTrigger>
            <TabsTrigger value="analisis" className="gap-1.5 text-xs">
              <BarChart3 className="h-3 w-3" />
              Análisis
            </TabsTrigger>
          </TabsList>

{/* Tab: Buscar */}
          <TabsContent value="buscar" className="space-y-4">
            {/* Route Nodes Visualization - Resultados de ruta */}
            <RouteNodes
              resultados={resultados}
              selectedAlgorithm={algoSeleccionado}
              ciudad={ciudad}
            />

            {/* Mensaje para ir al mapa */}
            {resultados.length === 0 && (
              <Card>
                <CardContent className="py-8 text-center text-muted-foreground">
                  <Map className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Ve al tab "Mapa" para seleccionar origen y destino</p>
                  <p className="text-xs mt-1">Los resultados aparecerán aquí</p>
                </CardContent>
              </Card>
            )}

            {/* Resultados Cards */}
            {resultados.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-muted-foreground">Resultados de Ruta</h3>
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
                            <span className="text-muted-foreground text-xs">Nodos expandidos:</span>
                            <span className="font-medium text-xs">{r.nodos_expandidos}</span>
                          </div>

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
              </div>
            )}
          </TabsContent>

          {/* Tab: Mapa */}
          <TabsContent value="mapa" className="space-y-4">
            {grafoCompleto ? (
              <GrafoVisual
                datosGrafo={grafoCompleto}
                onBuscarRutaInterurbana={async (origen, destino) => {
                  try {
                    const resultadosRuta = await buscarRuta({
                      origen,
                      destino,
                      ciudad: null,
                      hora,
                      dia_semana: dia,
                      tipo_vehiculo: vehiculo,
                      clima
                    });
                    if (resultadosRuta && resultadosRuta.length > 0) {
                      setResultados(resultadosRuta);
                      setAlgoSeleccionado(resultadosRuta[0].algoritmo);
                      setTab('buscar'); // Volver a la pestaña de resultados
                      return resultadosRuta[0];
                    }
                  } catch (err) {
                    console.error('Error buscando ruta inter-urbana:', err);
                  }
                  return null;
                }}
              />
            ) : (
              <Card>
                <CardContent className="py-8 text-center text-muted-foreground">
                  Cargando mapa...
                </CardContent>
              </Card>
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