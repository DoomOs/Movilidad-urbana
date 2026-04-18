import { useState, useEffect } from 'react';
import { buscarRuta, compararAlgoritmos, obtenerCiudades, obtenerCallesPorCiudad, predecirTiempo, obtenerAnalisisDatos } from './api';

function App() {
  const [tabActiva, setTabActiva] = useState('buscar');
  const [ciudades, setCiudades] = useState([]);
  const [calles, setCalles] = useState([]);
  const [origen, setOrigen] = useState('');
  const [destino, setDestino] = useState('');
  const [ciudadSeleccionada, setCiudadSeleccionada] = useState('');
  const [hora, setHora] = useState(12);
  const [diaSemana, setDiaSemana] = useState('Lunes');
  const [tipoVehiculo, setTipoVehiculo] = useState('automovil');
  const [clima, setClima] = useState('Despejado');
  
  const [resultados, setResultados] = useState(null);
  const [comparacion, setComparacion] = useState(null);
  const [prediccion, setPrediccion] = useState(null);
  const [analisis, setAnalisis] = useState(null);
  
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  // Cargar ciudades al iniciar
  useEffect(() => {
    cargarCiudades();
    cargarAnalisis();
  }, []);

  // Cargar calles cuando cambia la ciudad
  useEffect(() => {
    if (ciudadSeleccionada) {
      cargarCalles(ciudadSeleccionada);
    }
  }, [ciudadSeleccionada]);

  const cargarCiudades = async () => {
    try {
      const data = await obtenerCiudades();
      setCiudades(data.ciudades);
      if (data.ciudades.length > 0) {
        setCiudadSeleccionada(data.ciudades[0]);
      }
    } catch (err) {
      setError('Error al cargar ciudades: ' + err.message);
    }
  };

  const cargarCalles = async (ciudad) => {
    try {
      const data = await obtenerCallesPorCiudad(ciudad);
      setCalles(data.calles);
      if (data.calles.length > 0) {
        setOrigen(data.calles[0]);
        if (data.calles.length > 1) {
          setDestino(data.calles[1]);
        }
      }
    } catch (err) {
      setError('Error al cargar calles: ' + err.message);
    }
  };

  const cargarAnalisis = async () => {
    try {
      const data = await obtenerAnalisisDatos();
      setAnalisis(data);
    } catch (err) {
      console.error('Error al cargar análisis:', err);
    }
  };

  const handleBuscarRuta = async () => {
    if (!origen || !destino) {
      setError('Debe seleccionar origen y destino');
      return;
    }

    setCargando(true);
    setError(null);

    try {
      const datos = {
        origen,
        destino,
        hora,
        dia_semana: diaSemana,
        tipo_vehiculo: tipoVehiculo,
        clima,
      };

      const resultadosBusqueda = await buscarRuta(datos);
      setResultados(resultadosBusqueda);

      const comparacionData = await compararAlgoritmos(origen, destino);
      setComparacion(comparacionData);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al buscar ruta');
    } finally {
      setCargando(false);
    }
  };

  const handlePredecirTiempo = async () => {
    if (!origen || !destino) {
      setError('Debe seleccionar origen y destino para predecir');
      return;
    }

    setCargando(true);
    setError(null);

    try {
      // Obtener distancia aproximada de los resultados previos o usar valor por defecto
      const distancia = resultados ? resultados[0]?.distancia_total : 5.0;
      const prediccionData = await predecirTiempo(distancia, 'Medio', hora);
      setPrediccion(prediccionData);
    } catch (err) {
      setError('Error al predecir tiempo: ' + err.message);
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="app">
      <header>
        <div className="container">
          <h1>Sistema Inteligente de Recomendación de Rutas Urbanas</h1>
          <p>IA aplicada a movilidad urbana con búsqueda, lógica de predicados y machine learning</p>
        </div>
      </header>

      <div className="container">
        {error && <div className="error">{error}</div>}

        <div className="tabs">
          <button 
            className={`tab ${tabActiva === 'buscar' ? 'active' : ''}`}
            onClick={() => setTabActiva('buscar')}
          >
            Buscar Ruta
          </button>
          <button 
            className={`tab ${tabActiva === 'analisis' ? 'active' : ''}`}
            onClick={() => setTabActiva('analisis')}
          >
            Análisis de Datos
          </button>
        </div>

        {tabActiva === 'buscar' && (
          <>
            <div className="card">
              <h2>Parámetros del Viaje</h2>
              
              <div className="form-group">
                <label>Ciudad:</label>
                <select 
                  value={ciudadSeleccionada} 
                  onChange={(e) => setCiudadSeleccionada(e.target.value)}
                >
                  {ciudades.map((ciudad) => (
                    <option key={ciudad} value={ciudad}>{ciudad}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Origen:</label>
                <select value={origen} onChange={(e) => setOrigen(e.target.value)}>
                  {calles.map((calle) => (
                    <option key={calle} value={calle}>{calle}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Destino:</label>
                <select value={destino} onChange={(e) => setDestino(e.target.value)}>
                  {calles.map((calle) => (
                    <option key={calle} value={calle}>{calle}</option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
                <div className="form-group">
                  <label>Hora:</label>
                  <input 
                    type="number" 
                    min="0" 
                    max="23" 
                    value={hora} 
                    onChange={(e) => setHora(parseInt(e.target.value))}
                  />
                </div>

                <div className="form-group">
                  <label>Día:</label>
                  <select value={diaSemana} onChange={(e) => setDiaSemana(e.target.value)}>
                    {['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'].map((dia) => (
                      <option key={dia} value={dia}>{dia}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Vehículo:</label>
                  <select value={tipoVehiculo} onChange={(e) => setTipoVehiculo(e.target.value)}>
                    <option value="automovil">Automóvil</option>
                    <option value="bicicleta">Bicicleta</option>
                    <option value="motocicleta">Motocicleta</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Clima:</label>
                  <select value={clima} onChange={(e) => setClima(e.target.value)}>
                    <option value="Despejado">Despejado</option>
                    <option value="Nublado">Nublado</option>
                    <option value="Lluvia Ligera">Lluvia Ligera</option>
                    <option value="Lluvia Intensa">Lluvia Intensa</option>
                  </select>
                </div>
              </div>

              <button 
                className="btn" 
                onClick={handleBuscarRuta}
                disabled={cargando}
              >
                {cargando ? 'Buscando...' : 'Buscar Ruta Óptima'}
              </button>
            </div>

            {resultados && (
              <div className="card resultados">
                <h2>Resultados de Búsqueda</h2>
                
                {resultados.map((resultado, index) => (
                  <div key={index} className="ruta-card">
                    <h3>{resultado.algoritmo}</h3>
                    <div className="ruta-info">
                      <span><strong>Distancia:</strong> {resultado.distancia_total} km</span>
                      <span><strong>Tiempo:</strong> {resultado.tiempo_total} min</span>
                      {resultado.tiempo_ajustado && (
                        <span><strong>Tiempo Ajustado:</strong> {resultado.tiempo_ajustado} min</span>
                      )}
                      <span><strong>Nodos:</strong> {resultado.nodos_expandidos}</span>
                    </div>
                    <div className="ruta">
                      <strong>Ruta:</strong> {resultado.ruta.join(' → ')}
                    </div>
                    
                    {resultado.recomendaciones.length > 0 && (
                      <div className="recomendaciones">
                        <strong>Recomendaciones:</strong> {resultado.recomendaciones.join(', ')}
                      </div>
                    )}
                    
                    {resultado.advertencias.length > 0 && (
                      <div className="advertencias">
                        <strong>Advertencias:</strong> {resultado.advertencias.join(', ')}
                      </div>
                    )}
                  </div>
                ))}

                {comparacion && (
                  <div style={{ marginTop: '2rem' }}>
                    <h3>Comparación de Algoritmos</h3>
                    <table className="comparacion-table">
                      <thead>
                        <tr>
                          <th>Algoritmo</th>
                          <th>Tiempo (min)</th>
                          <th>Distancia (km)</th>
                          <th>Nodos Expandidos</th>
                        </tr>
                      </thead>
                      <tbody>
                        {comparacion.bfs && (
                          <tr className={comparacion.mejor_opcion === 'BFS' ? 'mejor-opcion' : ''}>
                            <td>BFS {comparacion.mejor_opcion === 'BFS' && '✓'}</td>
                            <td>{comparacion.bfs.tiempo}</td>
                            <td>{comparacion.bfs.distancia}</td>
                            <td>{comparacion.bfs.nodos_expandidos}</td>
                          </tr>
                        )}
                        {comparacion.dfs && (
                          <tr className={comparacion.mejor_opcion === 'DFS' ? 'mejor-opcion' : ''}>
                            <td>DFS {comparacion.mejor_opcion === 'DFS' && '✓'}</td>
                            <td>{comparacion.dfs.tiempo}</td>
                            <td>{comparacion.dfs.distancia}</td>
                            <td>{comparacion.dfs.nodos_expandidos}</td>
                          </tr>
                        )}
                        {comparacion.a_estrella && (
                          <tr className={comparacion.mejor_opcion === 'A*' ? 'mejor-opcion' : ''}>
                            <td>A* {comparacion.mejor_opcion === 'A*' && '✓'}</td>
                            <td>{comparacion.a_estrella.tiempo}</td>
                            <td>{comparacion.a_estrella.distancia}</td>
                            <td>{comparacion.a_estrella.nodos_expandidos}</td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                    {comparacion.razon && (
                      <p style={{ marginTop: '1rem', fontStyle: 'italic' }}>
                        <strong>Mejor opción:</strong> {comparacion.mejor_opcion} - {comparacion.razon}
                      </p>
                    )}
                  </div>
                )}

                <button 
                  className="btn" 
                  onClick={handlePredecirTiempo}
                  disabled={cargando}
                  style={{ marginTop: '1rem' }}
                >
                  Predecir Tiempo con ML
                </button>

                {prediccion && (
                  <div className="success" style={{ marginTop: '1rem' }}>
                    <strong>Predicción ML:</strong> {prediccion.tiempo_predicho} minutos 
                    (Confianza: {prediccion.confianza})
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {tabActiva === 'analisis' && analisis && (
          <div className="card">
            <h2>Análisis Exploratorio de Datos</h2>
            
            <div className="stats-grid">
              <div className="stat-card">
                <h3>{analisis.total_registros}</h3>
                <p>Registros Totales</p>
              </div>
              <div className="stat-card">
                <h3>{analisis.ciudades_disponibles.length}</h3>
                <p>Ciudades</p>
              </div>
              <div className="stat-card">
                <h3>{analisis.estadisticas_tiempo.promedio}</h3>
                <p>Tiempo Promedio (min)</p>
              </div>
              <div className="stat-card">
                <h3>{analisis.estadisticas_tiempo.maximo}</h3>
                <p>Tiempo Máximo (min)</p>
              </div>
            </div>

            <div style={{ marginTop: '2rem' }}>
              <h3>Estadísticas de Tráfico</h3>
              <table className="comparacion-table">
                <thead>
                  <tr>
                    <th>Nivel</th>
                    <th>Frecuencia</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(analisis.estadisticas_trafico).map(([nivel, frecuencia]) => (
                    <tr key={nivel}>
                      <td>{nivel}</td>
                      <td>{frecuencia}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div style={{ marginTop: '2rem' }}>
              <h3>Calles por Ciudad</h3>
              <table className="comparacion-table">
                <thead>
                  <tr>
                    <th>Ciudad</th>
                    <th>Número de Calles</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(analisis.calles_por_ciudad).map(([ciudad, numCalles]) => (
                    <tr key={ciudad}>
                      <td>{ciudad}</td>
                      <td>{numCalles}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
