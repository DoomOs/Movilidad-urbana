import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const obtenerCiudades = async () => {
  const response = await api.get('/ciudades');
  return response.data;
};

export const obtenerCallesPorCiudad = async (ciudad) => {
  const response = await api.get(`/calles/${encodeURIComponent(ciudad)}`);
  return response.data;
};

export const buscarRuta = async (datos) => {
  const response = await api.post('/buscar-ruta', datos);
  return response.data;
};

export const compararAlgoritmos = async (origen, destino) => {
  const response = await api.get('/comparar-algoritmos', {
    params: { origen, destino },
  });
  return response.data;
};

export const predecirTiempo = async (distancia, nivelTraico, hora) => {
  const response = await api.post('/predecir-tiempo', null, {
    params: {
      distancia,
      nivel_trafico: nivelTraico,
      hora,
    },
  });
  return response.data;
};

export const obtenerAnalisisDatos = async () => {
  const response = await api.get('/analisis-datos');
  return response.data;
};

export default api;
