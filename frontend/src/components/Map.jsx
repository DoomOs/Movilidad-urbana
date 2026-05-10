import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import { useEffect } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix default marker icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const algorithmColors = {
  'BFS': '#3b82f6',   // blue
  'DFS': '#a855f7',   // purple
  'A*': '#22c55e',    // green
};

export default function MapComponent({ center = [14.6349, -90.5069], zoom = 13, resultados = [], selectedAlgorithm = null }) {
  return (
    <MapContainer
      center={center}
      zoom={zoom}
      style={{ height: '100%', width: '100%', borderRadius: '0.5rem' }}
      className="z-0"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Draw routes for each algorithm */}
      {resultados.map((resultado) => {
        if (!resultado.coordenadas_ruta || resultado.coordenadas_ruta.length === 0) {
          return null;
        }

        const positions = resultado.coordenadas_ruta.map(coord => [coord.lat, coord.lng]);
        const color = algorithmColors[resultado.algoritmo] || '#666';
        const isSelected = selectedAlgorithm === resultado.algoritmo;

        return (
          <Polyline
            key={resultado.algoritmo}
            positions={positions}
            pathOptions={{
              color: color,
              weight: isSelected ? 6 : 3,
              opacity: isSelected ? 1 : 0.6,
            }}
          />
        );
      })}

      {/* Markers for start and end points */}
      {resultados.length > 0 && resultados[0]?.ruta && resultados[0].ruta.length >= 2 && (
        <>
          <Marker position={resultados[0].coordenadas_ruta?.[0] || center}>
            <Popup>Inicio</Popup>
          </Marker>
          <Marker position={resultados[0].coordenadas_ruta?.[resultados[0].coordenadas_ruta.length - 1] || center}>
            <Popup>Destino</Popup>
          </Marker>
        </>
      )}
    </MapContainer>
  );
}