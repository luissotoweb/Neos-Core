#🐍 Neos Core Backend

El corazón de nuestro sistema de gestión. Neos Core es una API robusta construida con Python y FastAPI, diseñada bajo una arquitectura modular y un modelo multi-tenant para el aislamiento estricto de datos entre clientes.

🚀 Inicialización del Entorno

1\. Requisitos Previos

Python 3.10+ (Recomendado 3.12+)

PostgreSQL instalado localmente o en un servidor accesible.

2\. Configuración del Proyecto

bash

\# 1. Clonar e ingresar al directorio

cd Neos-Core

\# 2. Crear entorno virtual

python -m venv .venv

\# 3. Activar entorno virtual

\# Windows:

.venv\\Scripts\\activate

\# Linux/Mac:

source .venv/bin/activate

\# 4. Instalar dependencias

pip install -r requirements.txt

3\. Ejecución del Servidor

Para iniciar el servidor en modo desarrollo con recarga automática:

bash

python -m uvicorn main:app --reload

El servidor estará disponible en: http://localhost:8000

🗂️ Estructura Modular del Proyecto

El proyecto ha sido refactorizado para separar responsabilidades y facilitar el mantenimiento:

text

Neos-Core/

├── neos\_core/

│ ├── api/

│ │ └── v1/

│ │ ├── endpoints/ # Lógica de rutas (Users, Tenants, Inventory)

│ │ └── api\_router.py # Concentrador de rutas V1

│ ├── database/

│ │ ├── models/ # Definición de tablas SQLAlchemy

│ │ ├── config.py # Conexión y sesión de DB

│ │ └── seed.py # Poblado inicial (Roles, etc.)

│ ├── security/ # JWT, hashing y dependencias de seguridad

│ ├── schemas/ # Modelos Pydantic (Validación de datos)

│ └── crud/ # Operaciones de base de datos

├── main.py # Punto de entrada y configuración de la App

└── requirements.txt

📚 Documentación de la API

FastAPI genera automáticamente documentación interactiva basada en los esquemas Pydantic:

📖 Swagger UI: http://localhost:8000/docs

📄 ReDoc: http://localhost:8000/redoc

Prefijo de API: Todas las rutas modulares se encuentran bajo el prefijo /api/v1/.

🔧 Configuración (Variables de Entorno)

Crea un archivo .env en la raíz del proyecto. No compartas tus credenciales reales.

env

DATABASE\_URL=postgresql://:@:/

SECRET\_KEY=tu\_clave\_secreta\_para\_jwt

ALGORITHM=HS256

ACCESS\_TOKEN\_EXPIRE\_MINUTES=30

✨ Características Implementadas

✅ Multi-tenancy: Aislamiento de datos mediante tenant\_id

✅ RBAC (Role Based Access Control): Jerarquía de permisos (SuperAdmin, Admin, Seller, etc.)

✅ Arquitectura Modular: Rutas y lógica CRUD desacopladas por dominio

✅ Autenticación JWT: Seguridad basada en tokens

✅ Seeding Automático: Creación de roles básicos al iniciar la aplicación

Desarrollado con ❤️ por el equipo Neos