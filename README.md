# 🐍 Neos Core Backend

El corazón de nuestro sistema de gestión. Neos Core es una API robusta construida con **Python** y **FastAPI**, utilizando **PostgreSQL** para la persistencia de datos. Su arquitectura soporta un modelo multi-tenant para aislar los datos de cada cliente.

---

## 🚀 Inicialización del Entorno

### 1. Requisitos Previos

Asegúrate de tener instalado:
- **Python 3.10+**
- **Docker Desktop** (Activo y en ejecución)
- **Entorno virtual** (`.venv`) creado y activado.

### 2. Base de Datos (PostgreSQL)

Utilizamos Docker para un entorno de base de datos reproducible y consistente.

| Comando                | Acción |
| :---                   | :--- |
| `docker compose up -d` | Inicia los contenedores de PostgreSQL. |
| `docker compose down`  | Detiene y elimina los contenedores. |

Para iniciar la base de datos, simplemente ejecuta:
```bash
docker compose up -d
```

> **Nota:** Asegúrate de que Docker Desktop esté ejecutándose antes de correr el comando.

### 3. Configuración del Entorno Virtual

Si es la primera vez que trabajas con el proyecto:

```bash
# Crear entorno virtual (si no existe)
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 4. Ejecución del Servidor

Con el entorno virtual activado y la base de datos corriendo:

```bash
# Iniciar servidor de desarrollo (con recarga automática)
uvicorn main:app --reload
```

El servidor estará disponible en: [http://localhost:8000](http://localhost:8000)

---

## 📚 Documentación de la API

FastAPI genera automáticamente documentación interactiva:

- **📖 Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **📄 ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🗂️ Estructura del Proyecto

```
neos-core-backend/
├── app/
│   ├── api/           # Endpoints y rutas
│   ├── core/          # Configuración y utilidades
│   ├── models/        # Modelos de datos SQLAlchemy
│   ├── schemas/       # Pydantic schemas
│   └── services/      # Lógica de negocio
├── .venv/             # Entorno virtual
├── main.py            # Punto de entrada
├── requirements.txt   # Dependencias
├── docker-compose.yml # Configuración Docker
└── .env               # Variables de entorno (crear)
```

---

## 🔧 Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/neos_core
SECRET_KEY=tu_clave_secreta_aqui
ENVIRONMENT=development
```

---

## 🐳 Docker Compose

Configuración del entorno con Docker:

```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: neos_core
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 🤝 Contribuir

1. Crea un fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## ✨ Características Principales

- ✅ **FastAPI** - Alto rendimiento, fácil de usar, documentación automática
- ✅ **PostgreSQL** - Base de datos robusta y confiable
- ✅ **SQLAlchemy** - ORM poderoso y flexible
- ✅ **Multi-tenant** - Aislamiento de datos por cliente
- ✅ **Autenticación JWT** - Seguridad integrada
- ✅ **Docker** - Entorno reproducible
- ✅ **Type Hints** - Código más mantenible y seguro

---

*Desarrollado con ❤️ por el equipo Neos*