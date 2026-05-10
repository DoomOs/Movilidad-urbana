import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

export const obtenerCiudades = async () => {
  const response = await api.get('/ciudades');
  return response.data;
};

export const obtenerCalles = async (ciudad) => {
  const response = await api.get(`/calles/${encodeURIComponent(ciudad)}`);
  return response.data;
};

export const buscarRuta = async (datos) => {
  const response = await api.post('/buscar-ruta', datos);
  return response.data;
};

export const compararAlgoritmos = async (origen, destino) => {
  const response = await api.get('/comparar-algoritmos', { params: { origen, destino } });
  return response.data;
};

export const predecirTiempo = async (distancia, nivelTrafico, hora) => {
  const response = await api.post('/predecir-tiempo', null, {
    params: { distancia, nivel_trafico: nivelTrafico, hora }
  });
  return response.data;
};

export const compararModelos = async (distancia, nivelTrafico, hora) => {
  const response = await api.get('/comparar-modelos', {
    params: { distancia, nivel_trafico: nivelTrafico, hora }
  });
  return response.data;
};

export const obtenerAnalisis = async () => {
  const response = await api.get('/analisis-datos');
  return response.data;
};

export const obtenerMetricasML = async () => {
  const response = await api.get('/metricas-ml');
  return response.data;
};

export const obtenerHistorial = async () => {
  const response = await api.get('/historial');
  return response.data;
};

export const verificarSalud = async () => {
  const response = await api.get('/salud');
  return response.data;
};

export default api;