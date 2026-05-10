"""
Configuración de base de datos SQLite para el proyecto.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "movilidad_guatemala.db"
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, DB_NAME)}"

# SQLite con uri especial para single file
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

# FK constraints para SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency para obtener sesión de DB."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializar base de datos."""
    Base.metadata.create_all(bind=engine)