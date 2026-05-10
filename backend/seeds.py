"""
Datos semilla para ciudades y calles de Guatemala.
"""
from models import Ciudad, Calle, RegistroTrafico, Nodo, Arista, NivelTrafico, CondicionClima, TipoVehiculo, DiaSemana
from database import SessionLocal
import random


# Coordenadas aproximadas de ciudades de Guatemala
COORDENADAS_CIUDADES = {
    "Ciudad de Guatemala": (14.6349, -90.5069),
    "Antigua Guatemala": (14.5586, -90.7295),
    "Quetzaltenango": (14.8347, -91.5189),
    "Escuintla": (14.2917, -90.7855),
    "Puerto San José": (13.9262, -90.8218),
    "Cobán": (15.4707, -90.3766),
    "Zacapa": (14.8077, -90.3220),
    "Chiquimula": (14.7953, -89.5450),
    "Retalhuleu": (14.5375, -91.6818),
    "Mazatenango": (14.3728, -91.6289),
}


CALLES_GUATEMALA = {
    "Ciudad de Guatemala": [
        "Avenida La Reforma",
        "Avenida Las Américas",
        "Avenida Simeon Cañas",
        "Boulevard Los Próceres",
        "Avenida La Independencia",
        "Avenida Las Charcas",
        "Boulevard Vista Hermosa",
        "Calzada La Paz",
        "Avenida del Estadio",
        "Calle del Montecristo",
        "Avenida华北",
        "Boulevard Gerónimo",
        "Avenida La Primaveral",
        "Calle del Porvenir",
        "Avenida Los Almendros",
    ],
    "Antigua Guatemala": [
        "Avenida del Centro",
        "Calle del Arco de Santa Catalina",
        "Avenida de la Recolección",
        "Calle de los Pasos",
        "Avenida Principal",
        "Calle de la Sexta",
        "Avenida de la Ermita",
        "Calle de San Francisco",
        "Avenida del Cerrito del Carmen",
        "Calle de los Remedios",
    ],
    "Quetzaltenango": [
        "Avenida Las Américas",
        "Calle Monte Carlo",
        "Boulevard Emilianense",
        "Avenida San Martín",
        "Avenida 4 de Diciembre",
        "Calle del Estadio",
        "Avenida Los Andes",
        "Calle del Mercado",
        "Avenida del Centro",
        "Boulevard Los Volcanes",
    ],
    "Escuintla": [
        "Avenida Carlos A. Montufar",
        "Boulevard Sur",
        "Avenida La Fama",
        "Avenida Las Palmeras",
        "Carretera Panamericana",
        "Calle del Mercado",
        "Avenida del Valle",
        "Boulevard industrial",
    ],
    "Puerto San José": [
        "Avenida del Puerto",
        "Calle Principal",
        "Avenida La Playa",
        "Boulevard Costero",
        "Calle de la Marina",
        "Avenida del Mar",
        "Calle del Puerto",
    ],
    "Cobán": [
        "Calle Real de Cobán",
        "Avenida La Primavera",
        "Calle del Calvario",
        "Avenida Los Cerezos",
        "Boulevard华北",
        "Calle del Mercado",
        "Avenida Santa María",
        "Avenida del Carmen",
    ],
    "Zacapa": [
        "Avenida La Paz",
        "Calle Real",
        "Boulevard El Campesino",
        "Avenida de las Flores",
        "Calle del Mercado",
        "Avenida San José",
        "Boulevard Zacapa",
    ],
    "Chiquimula": [
        "Avenida La Paz",
        "Calle Real",
        "Boulevard Chiquimula",
        "Calle del Centro",
        "Avenida Los Próceres",
        "Calle del Mercado",
        "Boulevard El Oriente",
    ],
    "Retalhuleu": [
        "Avenida 15 de Septiembre",
        "Calle Real",
        "Boulevard del Ferrocarril",
        "Avenida La Independencia",
        "Calle del Mercado",
        "Avenida del Centro",
        "Boulevard Retalhuleu",
    ],
    "Mazatenango": [
        "Avenida Carlos A. Montufar",
        "Calle Real",
        "Boulevard Sur",
        "Avenida La Fama",
        "Calle del Mercado Central",
        "Avenida del Valle",
        "Boulevard Mazatenango",
    ],
}


def seed_database():
    """Poblar la base de datos con datos de Guatemala."""
    db = SessionLocal()

    try:
        # Verificar si ya hay datos
        existing = db.query(Ciudad).first()
        if existing:
            print("La base de datos ya tiene datos. Saltando seed.")
            return

        print("Creando ciudades de Guatemala...")
        ciudades_map = {}

        for nombre, (lat, lng) in COORDENADAS_CIUDADES.items():
            # Determinar departamento
            dept_map = {
                "Ciudad de Guatemala": "Guatemala",
                "Antigua Guatemala": "Sacatepéquez",
                "Quetzaltenango": "Quetzaltenango",
                "Escuintla": "Escuintla",
                "Puerto San José": "Escuintla",
                "Cobán": "Alta Verapaz",
                "Zacapa": "Zacapa",
                "Chiquimula": "Chiquimula",
                "Retalhuleu": "Retalhuleu",
                "Mazatenango": "Suchitepéquez",
            }

            ciudad = Ciudad(
                nombre=nombre,
                departamento=dept_map.get(nombre, "Guatemala"),
                latitud=lat,
                longitud=lng
            )
            db.add(ciudad)
            db.flush()
            ciudades_map[nombre] = ciudad
            print(f"  + {nombre}")

        db.commit()
        print(f"  {len(ciudades_map)} ciudades creadas.\n")

        print("Creando calles para cada ciudad...")
        calles_map = {}

        for ciudad_nombre, calles_nombres in CALLES_GUATEMALA.items():
            ciudad = ciudades_map[ciudad_nombre]
            calles_list = []

            for i, nombre_calle in enumerate(calles_nombres):
                # Generar coordenadas pseudo-aleatorias basadas en la ciudad
                lat_offset = (random.random() - 0.5) * 0.02
                lng_offset = (random.random() - 0.5) * 0.02

                tipo = "avenida" if "Avenida" in nombre_calle or "Boulevard" in nombre_calle else "calle"
                if "Boulevard" in nombre_calle:
                    tipo = "boulevard"
                elif "Carretera" in nombre_calle:
                    tipo = "carretera"

                calle = Calle(
                    nombre=nombre_calle,
                    ciudad_id=ciudad.id,
                    latitud=ciudad.latitud + lat_offset,
                    longitud=ciudad.longitud + lng_offset,
                    tipo=tipo
                )
                db.add(calle)
                calles_list.append(calle)

            calles_map[ciudad_nombre] = calles_list
            print(f"  + {ciudad_nombre}: {len(calles_list)} calles")

        db.commit()
        print()

        print("Generando registros de tráfico (esto puede tardar un poco)...")

        # Generar registros de tráfico para cada ciudad
        trafic_options = list(NivelTrafico)
        clima_options = list(CondicionClima)
        vehiculo_options = list(TipoVehiculo)
        dia_options = list(DiaSemana)

        horas_pico_manana = [7, 8, 9]
        horas_pico_tarde = [17, 18, 19, 20]

        total_registros = 0

        for ciudad_nombre, calles in calles_map.items():
            ciudad = ciudades_map[ciudad_nombre]

            # Generar 20-30 registros por ciudad
            num_registros = random.randint(20, 30)

            for _ in range(num_registros):
                origen, destino = random.sample(calles, 2)

                # Distancia pseudo-aleatoria basada en índice
                idx_o = calles.index(origen)
                idx_d = calles.index(destino)
                diff = abs(idx_o - idx_d)
                distancia = max(1.5, min(25.0, diff * 2.5 + random.uniform(-1, 3)))

                # Hora y día
                hora = random.choice(list(range(24)))
                dia = random.choice(dia_options)

                # Determinar tráfico según hora y día
                es_fin_semana = dia in [DiaSemana.SABADO, DiaSemana.DOMINGO]
                if not es_fin_semana:
                    if hora in horas_pico_manana or hora in horas_pico_tarde:
                        trafico = random.choice([NivelTrafico.ALTO, NivelTrafico.MUY_ALTO])
                    elif 10 <= hora <= 16:
                        trafico = random.choice([NivelTrafico.MEDIO, NivelTrafico.ALTO])
                    else:
                        trafico = random.choice([NivelTrafico.BAJO, NivelTrafico.MEDIO])
                else:
                    if 11 <= hora <= 21:
                        trafico = random.choice([NivelTrafico.MEDIO, NivelTrafico.ALTO])
                    else:
                        trafico = NivelTrafico.BAJO

                clima = random.choice(clima_options)
                vehiculo = random.choice(vehiculo_options)

                # Calcular tiempo
                velocidades = {
                    NivelTrafico.BAJO: 50,
                    NivelTrafico.MEDIO: 35,
                    NivelTrafico.ALTO: 20,
                    NivelTrafico.MUY_ALTO: 12
                }
                velocidad = velocidades[trafico]

                factores_clima = {
                    CondicionClima.DESPEJADO: 1.0,
                    CondicionClima.NUBLADO: 1.05,
                    CondicionClima.LLUVIA_LIGERA: 1.2,
                    CondicionClima.LLUVIA_INTENSA: 1.5
                }
                factor_clima = factores_clima[clima]

                if hora in horas_pico_manana or hora in horas_pico_tarde:
                    factor_hora = 1.3
                elif 10 <= hora <= 16:
                    factor_hora = 1.1
                elif 21 <= hora or hora <= 5:
                    factor_hora = 0.9
                else:
                    factor_hora = 1.0

                tiempo_horas = distancia / (velocidad * factor_clima * factor_hora)
                tiempo_minutos = tiempo_horas * 60 * random.uniform(0.9, 1.1)

                registro = RegistroTrafico(
                    ciudad_id=ciudad.id,
                    origen_id=origen.id,
                    destino_id=destino.id,
                    distancia_km=round(distancia, 2),
                    trafico=trafico,
                    clima=clima,
                    hora=hora,
                    dia_semana=dia,
                    tiempo_estimado_min=round(tiempo_minutos, 2),
                    vehiculo=vehiculo
                )
                db.add(registro)
                total_registros += 1

        db.commit()
        print(f"  {total_registros} registros de tráfico creados.\n")

        print("Construyendo grafo de nodos y aristas...")

        # Crear nodos y aristas para el grafo
        nodos_creados = 0
        aristas_creadas = 0

        for ciudad_nombre, calles in calles_map.items():
            ciudad = ciudades_map[ciudad_nombre]

            for i, calle in enumerate(calles):
                nodo = Nodo(
                    nombre=calle.nombre,
                    ciudad_id=ciudad.id,
                    calle_origen_id=calle.id,
                    calle_destino_id=calle.id,
                    latitud=calle.latitud,
                    longitud=calle.longitud
                )
                db.add(nodo)
                nodos_creados += 1

        db.commit()

        # Obtener todos los nodos por ciudad
        nodos_por_ciudad = {}
        all_nodos = db.query(Nodo).all()
        for nodo in all_nodos:
            if nodo.ciudad_id not in nodos_por_ciudad:
                nodos_por_ciudad[nodo.ciudad_id] = []
            nodos_por_ciudad[nodo.ciudad_id].append(nodo)

        # Crear aristas entre nodos cercanos (mismo origen/destino en registros)
        registros = db.query(RegistroTrafico).all()
        aristas_set = set()

        for reg in registros:
            # Buscar nodos correspondientes
            nodo_origen = db.query(Nodo).filter(
                Nodo.calle_origen_id == reg.origen_id,
                Nodo.ciudad_id == reg.ciudad_id
            ).first()

            nodo_destino = db.query(Nodo).filter(
                Nodo.calle_destino_id == reg.destino_id,
                Nodo.ciudad_id == reg.ciudad_id
            ).first()

            if nodo_origen and nodo_destino and nodo_origen.id != nodo_destino.id:
                arista_key = (nodo_origen.id, nodo_destino.id)
                if arista_key not in aristas_set:
                    arista = Arista(
                        nodo_origen_id=nodo_origen.id,
                        nodo_destino_id=nodo_destino.id,
                        distancia_km=reg.distancia_km,
                        tiempo_min=reg.tiempo_estimado_min,
                        trafico=reg.trafico
                    )
                    db.add(arista)
                    aristas_set.add(arista_key)
                    aristas_set.add((nodo_destino.id, nodo_origen.id))  # Bidireccional

                    # Arista inversa
                    arista_inv = Arista(
                        nodo_origen_id=nodo_destino.id,
                        nodo_destino_id=nodo_origen.id,
                        distancia_km=reg.distancia_km,
                        tiempo_min=reg.tiempo_estimado_min,
                        trafico=reg.trafico
                    )
                    db.add(arista_inv)
                    aristas_creadas += 1

        db.commit()
        print(f"  {nodos_creados} nodos creados.")
        print(f"  {len(aristas_set)} aristas creadas (bidireccionales).\n")

        print("=== Base de datos Guatemala lista ===")
        print(f"  Ciudades: {len(ciudades_map)}")
        print(f"  Calles: {sum(len(c) for c in calles_map.values())}")
        print(f"  Registros: {total_registros}")
        print(f"  Nodos: {nodos_creados}")
        print(f"  Aristas: {aristas_creadas}")

    except Exception as e:
        print(f"Error durante el seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()