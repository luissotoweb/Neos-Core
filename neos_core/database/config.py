from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Definir la URL de Conexión
# Observa que el HOST es 'db', NO 'localhost', porque Docker resuelve el nombre del servicio.
# Esto es una buena práctica de ingeniería al trabajar con contenedores.
DATABASE_URL = "postgresql://neos_user:neos_pwd@localhost:5432/neos_db"

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