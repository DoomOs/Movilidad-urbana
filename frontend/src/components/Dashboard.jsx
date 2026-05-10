import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Badge } from './ui/badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Clock, MapPin, AlertTriangle } from 'lucide-react';

const COLORS = ['#22c55e', '#eab308', '#f97316', '#ef4444'];

export function StatsCards({ stats }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Registros Totales</CardTitle>
          <MapPin className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats?.total_registros || 0}</div>
          <p className="text-xs text-muted-foreground">en el dataset</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Ciudades</CardTitle>
          <MapPin className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats?.ciudades_disponibles?.length || 0}</div>
          <p className="text-xs text-muted-foreground">disponibles en GT</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Tiempo Promedio</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats?.estadisticas_tiempo?.promedio || 0} min</div>
          <p className="text-xs text-muted-foreground">tiempo medio de viaje</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Registros Recientes</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats?.registros_recientes?.length || 0}</div>
          <p className="text-xs text-muted-foreground">últimos registros</p>
        </CardContent>
      </Card>
    </div>
  );
}

export function TrafficChart({ data }) {
  if (!data) return null;

  const chartData = Object.entries(data).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Distribución de Tráfico</CardTitle>
        <CardDescription>Niveles de congestión en el dataset</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

export function TimeDistributionChart({ stats }) {
  if (!stats) return null;

  const data = [
    { name: 'Mínimo', value: stats.minimo },
    { name: 'Promedio', value: stats.promedio },
    { name: 'Mediana', value: stats.mediana },
    { name: 'Máximo', value: stats.maximo },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Distribución de Tiempos</CardTitle>
        <CardDescription>Estadísticas de tiempo de viaje (minutos)</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis label={{ value: 'Minutos', angle: -90, position: 'insideLeft' }} />
            <Tooltip formatter={(value) => [`${value} min`, 'Tiempo']} />
            <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

export function StreetsByCityChart({ data }) {
  if (!data) return null;

  const chartData = Object.entries(data).map(([ciudad, count]) => ({
    name: ciudad.replace('Ciudad de Guatemala', 'Guatemala City').replace('Antigua Guatemala', 'Antigua'),
    count,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Calles por Ciudad</CardTitle>
        <CardDescription>Cantidad de calles en cada ciudad</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={chartData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="name" type="category" width={100} tick={{ fontSize: 12 }} />
            <Tooltip formatter={(value) => [value, 'Calles']} />
            <Bar dataKey="count" fill="#22c55e" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

export function MLMetricsChart({ metricas }) {
  if (!metricas) return null;

  const chartData = Object.entries(metricas).map(([modelo, m]) => ({
    name: modelo.replace('_', ' ').replace('gradient boosting', 'GB').replace('random forest', 'RF').replace('regresion lineal', 'LR'),
    r2: m.r2,
    mae: m.mae,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Métricas de Modelos ML</CardTitle>
        <CardDescription>Comparación de rendimiento de modelos</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {chartData.map((item) => (
            <div key={item.name} className="flex items-center justify-between">
              <div className="flex-1">
                <div className="text-sm font-medium capitalize">{item.name}</div>
                <div className="flex gap-4 mt-1">
                  <Badge variant="outline">R²: {item.r2?.toFixed(3) || 'N/A'}</Badge>
                  <Badge variant="outline">MAE: {item.mae?.toFixed(2) || 'N/A'} min</Badge>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export function RecentRecordsTable({ registros }) {
  if (!registros || registros.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Registros Recientes</CardTitle>
        <CardDescription>Últimas rutas en el dataset</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-2">Origen</th>
                <th className="text-left py-2 px-2">Destino</th>
                <th className="text-right py-2 px-2">Dist (km)</th>
                <th className="text-right py-2 px-2">Tiempo (min)</th>
                <th className="text-center py-2 px-2">Tráfico</th>
              </tr>
            </thead>
            <tbody>
              {registros.slice(0, 8).map((reg, i) => (
                <tr key={i} className="border-b hover:bg-muted/50">
                  <td className="py-2 px-2 truncate max-w-[120px]">{reg.origen}</td>
                  <td className="py-2 px-2 truncate max-w-[120px]">{reg.destino}</td>
                  <td className="py-2 px-2 text-right">{reg.distancia_km}</td>
                  <td className="py-2 px-2 text-right">{reg.tiempo_min?.toFixed(1)}</td>
                  <td className="py-2 px-2 text-center">
                    <Badge
                      variant={
                        reg.trafico === 'Muy Alto' ? 'destructive' :
                        reg.trafico === 'Alto' ? 'warning' :
                        reg.trafico === 'Medio' ? 'info' : 'success'
                      }
                    >
                      {reg.trafico}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}