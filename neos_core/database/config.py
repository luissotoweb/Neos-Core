import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Definir la URL de Conexión
# Valor por defecto alineado con docker-compose.yml y el README.
# Si ejecutas la app dentro de Docker, reemplaza "localhost" por "db".
DEFAULT_DATABASE_URL = "postgresql://neos_user:123456@localhost:5434/neos_db"
_database_url = os.getenv("DATABASE_URL")
DATABASE_URL = _database_url if _database_url else DEFAULT_DATABASE_URL

# 2. Crear el Motor (Engine)
# El 'engine' es el punto de partida de la conexión con la base de datos.
engine = create_engine(DATABASE_URL)

# 3. Crear el SesionMaker
# SessionLocal es la clase que usaremos para crear cada sesión de base de datos.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base Declarativa
# Base es la clase de la que heredarán nuestros modelos de Python para convertirse en tablas.
Base = declarative_base()

# FUNCIÓN GENERADORA PARA INYECCIÓN DE DEPENDENCIA
def get_db():
    """
    Función que crea una nueva sesión de base de datos para cada petición,
    asegurando que se cierre limpiamente al finalizar o en caso de error.
    """
    db = SessionLocal()
    try:
        # Entrega la sesión a la función de ruta (yield)
        yield db
    finally:
        # Cierra la conexión después de que se envía la respuesta (finally)
        db.close()
