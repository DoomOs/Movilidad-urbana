import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { MapPin, Navigation, ArrowRight } from 'lucide-react';

export default function RouteNodes({ resultados = [], selectedAlgorithm = null, ciudad = '' }) {
  if (resultados.length === 0) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <Navigation className="h-4 w-4" />
            Ruta Calculada
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
            <MapPin className="h-8 w-8 mb-2 opacity-50" />
            <p className="text-sm">Busca una ruta para ver los nodos</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Get the selected algorithm's route or the first one
  const resultadoSeleccionado = selectedAlgorithm
    ? resultados.find(r => r.algoritmo === selectedAlgorithm) || resultados[0]
    : resultados[0];

  const ruta = resultadoSeleccionado?.ruta || [];
  const tiempoAjustado = resultadoSeleccionado?.tiempo_ajustado;
  const tiempoBase = resultadoSeleccionado?.tiempo_total;
  const distancia = resultadoSeleccionado?.distancia_total;
  const algColor = {
    'BFS': 'bg-blue-500',
    'DFS': 'bg-purple-500',
    'A*': 'bg-green-500'
  }[resultadoSeleccionado?.algoritmo] || 'bg-gray-500';

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <Navigation className="h-4 w-4" />
            Ruta en {ciudad || 'Guatemala'}
          </CardTitle>
          <Badge className={`${algColor} text-white text-xs`}>
            {resultadoSeleccionado?.algoritmo}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Stats */}
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="p-2 bg-muted rounded-lg">
            <p className="text-[10px] text-muted-foreground">Distancia</p>
            <p className="text-sm font-bold">{distancia} km</p>
          </div>
          <div className="p-2 bg-muted rounded-lg">
            <p className="text-[10px] text-muted-foreground">Tiempo Base</p>
            <p className="text-sm font-bold">{Math.round(tiempoBase)} min</p>
          </div>
          <div className="p-2 bg-muted rounded-lg border border-primary">
            <p className="text-[10px] text-muted-foreground">Ajustado</p>
            <p className="text-sm font-bold text-primary">{Math.round(tiempoAjustado)} min</p>
          </div>
        </div>

        {/* Algorithm selector buttons */}
        <div className="flex gap-2">
          {resultados.map((r) => (
            <button
              key={r.algoritmo}
              onClick={() => {}}
              className={`flex-1 py-1.5 px-2 rounded text-xs font-medium transition ${
                selectedAlgorithm === r.algoritmo || (!selectedAlgorithm && r.algoritmo === resultadoSeleccionado?.algoritmo)
                  ? 'ring-2 ring-primary'
                  : 'opacity-60 hover:opacity-100'
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

        {/* Node path visualization */}
        <div className="space-y-1">
          <p className="text-xs font-medium text-muted-foreground mb-2">
            Nodos de la Ruta ({ruta.length} puntos)
          </p>
          <div className="flex flex-col gap-1">
            {ruta.map((nodo, index) => {
              const isFirst = index === 0;
              const isLast = index === ruta.length - 1;
              return (
                <div key={index} className="flex items-center gap-2">
                  {/* Node indicator */}
                  <div className={`flex items-center justify-center w-6 h-6 rounded-full text-[10px] font-bold text-white shrink-0 ${
                    isFirst ? 'bg-green-500' : isLast ? 'bg-red-500' : 'bg-primary'
                  }`}>
                    {isFirst ? 'I' : isLast ? 'F' : index + 1}
                  </div>
                  {/* Node name */}
                  <div className={`flex-1 py-1.5 px-2 rounded text-xs font-medium ${
                    isFirst || isLast ? 'bg-muted' : ''
                  }`}>
                    {nodo}
                  </div>
                  {/* Connector line */}
                  {!isLast && (
                    <div className="absolute left-3 top-8 w-0.5 h-4 bg-border" style={{ marginTop: index * 28 }} />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Algorithm comparison */}
        {resultados.length > 1 && (
          <div className="pt-3 border-t">
            <p className="text-xs font-medium text-muted-foreground mb-2">Comparación de Algoritmos</p>
            <div className="grid grid-cols-3 gap-2 text-center">
              {resultados.map((r) => (
                <div key={r.algoritmo} className="p-2 bg-muted rounded">
                  <p className="text-[10px] text-muted-foreground">{r.algoritmo}</p>
                  <p className="text-sm font-bold">{Math.round(r.tiempo_total)} min</p>
                  <p className="text-[10px] text-muted-foreground">{r.nodos_expandidos} nodos</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}