import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import { useEffect } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const COLORS = {
  'BFS': '#3b82f6',
  'DFS': '#a855f7',
  'A*': '#22c55e',
};

const START_ICON = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
  iconRetinaUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

const END_ICON = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  iconRetinaUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

function MapUpdater({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
}

export default function MapComponent({ center = [14.6349, -90.5069], zoom = 13, resultados = [], selectedAlgorithm = null }) {
  const getPositions = (coords) => {
    if (!coords || coords.length === 0) return [];
    return coords.map(c => [c.lat, c.lng]);
  };

  const hasRoutes = resultados.some(r => r.coordenadas_ruta && r.coordenadas_ruta.length > 0);

  return (
    <MapContainer
      center={center}
      zoom={zoom}
      style={{ height: '100%', width: '100%' }}
      className="z-0"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <MapUpdater center={center} zoom={zoom} />

      {hasRoutes && resultados.map((resultado) => {
        const positions = getPositions(resultado.coordenadas_ruta);
        if (positions.length < 2) return null;

        const color = COLORS[resultado.algoritmo] || '#666';
        const isSelected = selectedAlgorithm === resultado.algoritmo;
        const weight = isSelected ? 5 : 2;
        const opacity = isSelected ? 1 : 0.5;

        return (
          <Polyline
            key={resultado.algoritmo}
            positions={positions}
            pathOptions={{ color, weight, opacity }}
          />
        );
      })}

      {hasRoutes && resultados[0]?.coordenadas_ruta?.length >= 2 && (
        <>
          <Marker
            position={resultados[0].coordenadas_ruta[0]}
            icon={START_ICON}
          >
            <Popup>Inicio</Popup>
          </Marker>
          <Marker
            position={resultados[0].coordenadas_ruta[resultados[0].coordenadas_ruta.length - 1]}
            icon={END_ICON}
          >
            <Popup>Destino</Popup>
          </Marker>
        </>
      )}
    </MapContainer>
  );
}