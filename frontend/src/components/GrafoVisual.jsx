import { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { ArrowRight, RefreshCw, MapPin } from 'lucide-react';

/**
 * GrafoVisual - Visualización del grafo de rutas de Guatemala
 * Muestra nodos (ciudades y calles) y aristas (conexiones) con capacidad de buscar rutas.
 */
export default function GrafoVisual({ datosGrafo, onBuscarRutaInterurbana }) {
  const [nodos, setNodos] = useState([]);
  const [aristas, setAristas] = useState([]);
  const [origen, setOrigen] = useState('');
  const [destino, setDestino] = useState('');
  const [rutaCalculada, setRutaCalculada] = useState(null);

  useEffect(() => {
    if (datosGrafo) {
      setNodos(datosGrafo.nodos || []);
      setAristas(datosGrafo.aristas || []);
    }
  }, [datosGrafo]);

  // Obtener solo nodos ciudad (para selects)
  const nodosCiudad = useMemo(() => {
    return nodos.filter(n => n.es_ciudad);
  }, [nodos]);

  // Ciudades únicas
  const ciudades = useMemo(() => {
    return [...new Set(nodosCiudad.map(n => n.ciudad))];
  }, [nodosCiudad]);

  // Calcular posición SVG basada en lat/lng
  const positionFromLatLng = (lat, lng) => {
    // Rango lat: ~13.5 a 15.5
    // Rango lng: ~-92 a -89
    const x = ((lng + 92) / 3) * 400;
    const y = ((15.5 - lat) / 2) * 300;
    return { x: Math.max(30, Math.min(370, x)), y: Math.max(20, Math.min(280, y)) };
  };

  // Dibujar aristas
  const aristasLines = useMemo(() => {
    return aristas.map((arista, i) => {
      const nodoOrigen = nodos.find(n => n.nombre === arista.origen);
      const nodoDestino = nodos.find(n => n.nombre === arista.destino);
      if (!nodoOrigen || !nodoDestino) return null;

      const posOrigen = positionFromLatLng(nodoOrigen.lat, nodoOrigen.lng);
      const posDestino = positionFromLatLng(nodoDestino.lat, nodoDestino.lng);

      const esRuta = rutaCalculada && rutaCalculada.ruta &&
        rutaCalculada.ruta.includes(nodoOrigen.nombre) &&
        rutaCalculada.ruta.includes(nodoDestino.nombre);

      return (
        <line
          key={`arista-${i}`}
          x1={posOrigen.x}
          y1={posOrigen.y}
          x2={posDestino.x}
          y2={posDestino.y}
          stroke={esRuta ? '#3b82f6' : '#6b7280'}
          strokeWidth={esRuta ? 3 : 1}
          strokeOpacity={esRuta ? 1 : 0.4}
          markerEnd={esRuta ? 'url(#arrowhead-blue)' : undefined}
        />
      );
    });
  }, [aristas, nodos, rutaCalculada]);

  // Dibujar nodos
  const nodosElements = useMemo(() => {
    return nodosCiudad.map((nodo, i) => {
      const pos = positionFromLatLng(nodo.lat, nodo.lng);
      const esOrigen = origen === nodo.ciudad;
      const esDestino = destino === nodo.ciudad;
      const enRuta = rutaCalculada?.ruta?.includes(nodo.nombre);

      return (
        <g key={`nodo-${i}`} transform={`translate(${pos.x}, ${pos.y})`}>
          {/* Círculo del nodo */}
          <circle
            r={esOrigen || esDestino ? 16 : nodo.es_ciudad ? 12 : 6}
            fill={esOrigen ? '#22c55e' : esDestino ? '#ef4444' : enRuta ? '#3b82f6' : '#8b5cf6'}
            stroke={esOrigen || esDestino ? 'white' : 'none'}
            strokeWidth={2}
          />
          {/* Etiqueta ciudad */}
          <text
            y={nodo.es_ciudad ? 28 : 18}
            textAnchor="middle"
            fontSize={nodo.es_ciudad ? 9 : 7}
            fill="#e5e7eb"
            fontWeight={nodo.es_ciudad ? '600' : '400'}
          >
            {nodo.ciudad}
          </text>
          {/* Etiqueta nodo */}
          {!nodo.es_ciudad && (
            <text
              y={-12}
              textAnchor="middle"
              fontSize={6}
              fill="#9ca3af"
            >
              {nodo.nombre.substring(0, 15)}
            </text>
          )}
        </g>
      );
    });
  }, [nodosCiudad, origen, destino, rutaCalculada]);

  const handleCalcularRuta = async () => {
    if (!origen || !destino || origen === destino) return;

    // Buscar el nodo ciudad de origen y destino
    const nodoOrigen = nodos.find(n => n.ciudad === origen && n.es_ciudad);
    const nodoDestino = nodos.find(n => n.ciudad === destino && n.es_ciudad);

    if (!nodoOrigen || !nodoDestino) {
      alert('No se encontró el nodo para la ruta seleccionada');
      return;
    }

    // Llamar a la búsqueda de ruta usando el nodo ciudad
    if (onBuscarRutaInterurbana) {
      const resultado = await onBuscarRutaInterurbana(nodoOrigen.nombre, nodoDestino.nombre);
      if (resultado) {
        setRutaCalculada(resultado);
      }
    }
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <MapPin className="h-4 w-4" />
          Mapa de Rutas - Guatemala
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Selector de origen/destino */}
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-muted-foreground">Ciudad Origen</label>
            <Select value={origen} onValueChange={setOrigen}>
              <SelectTrigger className="h-9">
                <SelectValue placeholder="Seleccionar origen" />
              </SelectTrigger>
              <SelectContent>
                {ciudades.map(c => (
                  <SelectItem key={c} value={c}>{c}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-muted-foreground">Ciudad Destino</label>
            <Select value={destino} onValueChange={setDestino}>
              <SelectTrigger className="h-9">
                <SelectValue placeholder="Seleccionar destino" />
              </SelectTrigger>
              <SelectContent>
                {ciudades.filter(c => c !== origen).map(c => (
                  <SelectItem key={c} value={c}>{c}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <Button
          onClick={handleCalcularRuta}
          disabled={!origen || !destino || origen === destino}
          className="w-full"
          size="sm"
        >
          <ArrowRight className="h-4 w-4 mr-1" />
          Calcular Ruta
        </Button>

        {/* Leyenda */}
        <div className="flex flex-wrap gap-2 text-xs">
          <Badge variant="outline" className="gap-1">
            <span className="w-2 h-2 rounded-full bg-purple-500"></span>
            Ciudad
          </Badge>
          <Badge variant="outline" className="gap-1">
            <span className="w-2 h-2 rounded-full bg-green-500"></span>
            Origen
          </Badge>
          <Badge variant="outline" className="gap-1">
            <span className="w-2 h-2 rounded-full bg-red-500"></span>
            Destino
          </Badge>
          <Badge variant="outline" className="gap-1">
            <span className="w-3 h-0.5 bg-blue-500"></span>
            Ruta
          </Badge>
        </div>

        {/* SVG del grafo */}
        <div className="bg-slate-900/50 rounded-md p-2 overflow-hidden">
          <svg viewBox="0 0 400 300" className="w-full h-48">
            <defs>
              <marker
                id="arrowhead-blue"
                markerWidth="10"
                markerHeight="7"
                refX="9"
                refY="3.5"
                orient="auto"
              >
                <polygon points="0 0, 10 3.5, 0 7" fill="#3b82f6" />
              </marker>
            </defs>

            {/* Grid de fondo */}
            <pattern id="grid" width="40" height="30" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 30" fill="none" stroke="#374151" strokeWidth="0.5" strokeOpacity="0.5" />
            </pattern>
            <rect width="100%" height="100%" fill="url(#grid)" />

            {/* Aristas */}
            {aristasLines}

            {/* Nodos */}
            {nodosElements}
          </svg>
        </div>

        {/* Info del grafo */}
        <div className="text-xs text-muted-foreground flex justify-between">
          <span>Nodos: {nodos.length}</span>
          <span>Aristas: {aristas.length}</span>
          {rutaCalculada && (
            <Badge variant="success" className="text-[10px]">
              Ruta: {rutaCalculada.distancia_total} km
            </Badge>
          )}
        </div>

        {/* Detalles de la ruta calculada */}
        {rutaCalculada && (
          <div className="bg-muted/50 rounded-md p-3 space-y-2">
            <h4 className="text-sm font-medium">Ruta: {origen} → {destino}</h4>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div>
                <span className="text-muted-foreground">Distancia:</span>
                <span className="ml-1 font-medium">{rutaCalculada.distancia_total} km</span>
              </div>
              <div>
                <span className="text-muted-foreground">Tiempo:</span>
                <span className="ml-1 font-medium">{Math.round(rutaCalculada.tiempo_total)} min</span>
              </div>
              <div>
                <span className="text-muted-foreground">Nodos:</span>
                <span className="ml-1 font-medium">{rutaCalculada.ruta?.length || 0}</span>
              </div>
            </div>
            {rutaCalculada.ruta && (
              <div className="text-xs">
                <span className="text-muted-foreground">Camino: </span>
                <span className="text-foreground font-mono">
                  {rutaCalculada.ruta.map(n => {
                    const esCiudad = n.startsWith('CIUDAD_');
                    return esCiudad ? n.replace('CIUDAD_', '') : n;
                  }).join(' → ')}
                </span>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}