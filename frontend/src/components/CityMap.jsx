import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { useEffect } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const GUATEMALA_CENTER = [15.5, -90.23];
const ZOOM_GUATEMALA = 7;
const ZOOM_CITY = 12;

function MapController({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom, { animate: true });
  }, [center, zoom, map]);
  return null;
}

export default function CityMap({ cities = [], selectedCity = null, onCitySelect = null }) {
  // If we have cities with coordinates, use them
  const citiesWithCoords = cities.filter(c => c.latitud && c.longitud);

  return (
    <MapContainer
      center={GUATEMALA_CENTER}
      zoom={ZOOM_GUATEMALA}
      style={{ height: '100%', width: '100%' }}
      className="rounded-md"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Show all cities as markers */}
      {citiesWithCoords.map((city) => {
        const isSelected = selectedCity === city.nombre;
        const size = isSelected ? [32, 32] : [25, 25];
        const icon = L.divIcon({
          className: 'custom-marker',
          html: `
            <div style="
              width: ${size[0]}px;
              height: ${size[1]}px;
              background-color: ${isSelected ? '#3b82f6' : '#22c55e'};
              border: 2px solid white;
              border-radius: 50%;
              box-shadow: 0 2px 4px rgba(0,0,0,0.3);
              display: flex;
              align-items: center;
              justify-content: center;
              color: white;
              font-weight: bold;
              font-size: ${isSelected ? '12px' : '10px'};
            ">
              ${isSelected ? '★' : city.id || ''}
            </div>
          `,
          iconSize: size,
          iconAnchor: [size[0] / 2, size[1] / 2],
        });

        return (
          <Marker
            key={city.id}
            position={[city.latitud, city.longitud]}
            icon={icon}
            eventHandlers={{
              click: () => onCitySelect?.(city.nombre),
            }}
          >
            <Popup>
              <div className="text-sm">
                <p className="font-bold">{city.nombre}</p>
                <p className="text-xs text-gray-500">{city.departamento}</p>
                <p className="text-xs mt-1">{city.num_calles || 0} calles</p>
              </div>
            </Popup>
          </Marker>
        );
      })}

      {/* Center on selected city */}
      {selectedCity && citiesWithCoords.length > 0 && (() => {
        const city = citiesWithCoords.find(c => c.nombre === selectedCity);
        if (city) {
          return <MapController center={[city.latitud, city.longitud]} zoom={ZOOM_CITY} />;
        }
        return null;
      })()}
    </MapContainer>
  );
}