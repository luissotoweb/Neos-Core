# 🐍 Neos Core Backend

El corazón de nuestro sistema de gestión. **Neos Core** es una API robusta construida con Python y FastAPI, diseñada bajo una arquitectura modular y un modelo multi-tenant para el aislamiento estricto de datos entre clientes.

---

## 🚀 Inicialización del Entorno

### 1. Requisitos Previos

- **Python 3.10+** (Recomendado 3.12+)
- **PostgreSQL** instalado localmente o en un servidor accesible
- **Git** para clonar el repositorio

### 2. Configuración del Proyecto

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/Neos-Core.git
cd Neos-Core

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar variables de entorno
# Copiar .env.example y editar .env con tus credenciales de PostgreSQL
```

### 3. Configurar Variables de Entorno

Crear archivo `.env` en la raíz:

```env
# Base de Datos (si usas docker-compose el puerto expuesto es 5434)
DATABASE_URL=postgresql://tu_usuario:tu_password@localhost:5434/neos_db

# Seguridad (SECRET_KEY es obligatoria y debe ser segura)
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Inicialización de Base de Datos (Primera vez)

```bash
# Opción 1: Script automatizado (Python)
# Las dependencias necesarias ya están listadas en requirements.txt
python init_system.py --skip-drop-create --no-confirm

# Opción 3: Manual
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
python neos_core/database/seed.py
```

### 5. Ejecución del Servidor

```bash
# Modo desarrollo (con recarga automática)
python -m uvicorn main:app --reload

# El servidor estará disponible en:
# http://localhost:8000
```

---

## 🧭 Onboarding desde cero

Guía rápida para levantar el proyecto desde una máquina nueva.

### 1) Clonado, entorno virtual e instalación de dependencias

```bash
git clone https://github.com/tu-usuario/Neos-Core.git
cd Neos-Core

python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### 2) Opción local con `docker-compose.yml` (PostgreSQL)

El archivo `docker-compose.yml` ya levanta PostgreSQL con credenciales predefinidas.

```bash
docker compose up -d
```

**PostgreSQL local (docker-compose):**
- Host: `localhost`
- Puerto: `5434`
- Base de datos: `neos_db`
- Usuario: `neos_user`
- Password: `123456`

### 3) Crear `.env`

Crear el archivo `.env` en la raíz con los valores mínimos:

```env
DATABASE_URL=postgresql://neos_user:123456@localhost:5434/neos_db
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> Nota: Ajusta `DATABASE_URL` si usas una base local diferente o un entorno remoto.  
> `SECRET_KEY` es obligatoria y debe ser un secreto real (ej. `openssl rand -hex 32`).

---

## ☁️ Migración/Despliegue en AWS (EC2 + systemd)

Esta ruta describe un despliegue clásico sobre **EC2** usando **systemd** para mantener el servicio.

### 1) Crear base de datos en RDS (PostgreSQL)

1. Crear una instancia RDS PostgreSQL (por ejemplo, `db.t3.micro` en desarrollo).
2. Definir usuario, contraseña y base de datos.
3. Habilitar acceso desde la VPC/subred donde vive tu EC2.

**Ejemplo de `DATABASE_URL`:**

```
postgresql://<usuario>:<password>@<endpoint-rds>:5432/<database>
```

### 2) Configurar variables de entorno en EC2 (systemd)

En EC2, crear un archivo de entorno (por ejemplo `/etc/neos-core.env`) y agregar:

```env
DATABASE_URL=postgresql://<usuario>:<password>@<endpoint-rds>:5432/<database>
SECRET_KEY=<secreto-produccion>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Ejemplo de unidad `systemd` (archivo `/etc/systemd/system/neos-core.service`):

```ini
[Unit]
Description=Neos Core API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/Neos-Core
EnvironmentFile=/etc/neos-core.env
ExecStart=/opt/Neos-Core/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Activar el servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl enable neos-core
sudo systemctl start neos-core
sudo systemctl status neos-core
```

### 3) Migraciones y seeding inicial

En el servidor (con `.env` cargado):

```bash
alembic upgrade head
python init_system.py
```

> ⚠️ **Producción:** evitar operaciones que hagan `drop` o borren datos. Usa migraciones incrementales y revisa cualquier script de inicialización antes de ejecutarlo.

### 4) Puertos, seguridad y observabilidad

- **Puertos:** expone `8000` en la instancia EC2 (o detrás de Nginx/ALB).
- **Security Groups:** permitir solo tráfico necesario:
  - Inbound `8000` (o `80/443` si hay reverse proxy).
  - RDS `5432` accesible únicamente desde el Security Group de la EC2.
- **Observabilidad:** revisar logs con `journalctl -u neos-core -f` y configurar rotación/forwarding a CloudWatch si es producción.

---

## 📚 Documentación de la API

FastAPI genera automáticamente documentación interactiva:

- **📖 Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **📄 ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

**Prefijo de API:** Todas las rutas modulares se encuentran bajo `/api/v1/`

---

## 📘 Documentación Funcional

Consulta la especificación funcional y el roadmap en [docs/nexus-pyme.md](docs/nexus-pyme.md).

---

## 🧭 Alcance del Repositorio (Backend-only)

Este repositorio contiene **solo el backend** (API, modelos y lógica de negocio). La interfaz web/PWA y cualquier frontend se gestionan en proyectos separados para evitar ambigüedad sobre responsabilidades y entregables.

---

## 🗂️ Estructura Modular del Proyecto

```
Neos-Core/
├── neos_core/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/          # Rutas de la API
│   │       │   ├── tenant_routes.py
│   │       │   ├── user_routes.py
│   │       │   ├── product_routes.py
│   │       │   ├── client_routes.py
│   │       │   ├── config_routes.py
│   │       │   └── sales_routes.py  # ⭐ NUEVO
│   │       └── api_router.py
│   ├── database/
│   │   ├── models/                 # Modelos SQLAlchemy
│   │   │   ├── tenant_model.py
│   │   │   ├── user_model.py
│   │   │   ├── product_model.py
│   │   │   ├── client_model.py
│   │   │   ├── sales_model.py      # ⭐ NUEVO
│   │   │   └── ...
│   │   ├── config.py               # Conexión de DB
│   │   └── seed.py                 # Datos iniciales
│   ├── security/                   # JWT, hashing, permisos
│   ├── schemas/                    # Validación Pydantic
│   └── crud/                       # Operaciones de DB
│   └── tests/                      # Tests unitarios
├── alembic/                        # Migraciones
├── main.py                         # Punto de entrada
├── .env.example
├── requirements.txt
└── README.md
```

---

## ✨ Características Implementadas

### ✅ Core del Sistema
- ✅ **Multi-tenancy**: Aislamiento estricto de datos mediante `tenant_id`
- ✅ **RBAC (Role Based Access Control)**: Jerarquía de permisos (SuperAdmin, Admin, Seller, Inventory, Accountant)
- ✅ **Arquitectura Modular**: Rutas y lógica CRUD desacopladas por dominio
- ✅ **Autenticación JWT**: Seguridad basada en tokens con expiración
- ✅ **Seeding Automático**: Creación de roles y datos básicos al iniciar

### ✅ Módulos Funcionales

#### 🏢 Gestión de Tenants (Empresas)
- Creación exclusiva por SuperAdmin
- Configuración de facturación electrónica (activable/desactivable)
- Aislamiento completo de datos

#### 👤 Gestión de Usuarios
- CRUD completo con hasheo de contraseñas (bcrypt)
- Asignación de roles y permisos
- Visibilidad limitada por tenant

#### 📦 Inventario (Productos)
- CRUD completo con control de stock
- Soporte para atributos dinámicos (JSONB)
- Búsqueda por SKU y código de barras
- Alertas de stock bajo
- Precisión monetaria con `Decimal` (no `Float`)

#### 🤝 Gestión de Clientes
- Alta con validación fiscal
- Unicidad de identificación por tenant

#### 💰 Configuración
- **Monedas**: Gestión global por SuperAdmin
- **Puntos de Venta**: Configuración por tenant

#### 🛒 **Módulo de Ventas** ⭐ NUEVO
- ✅ Creación de ventas con múltiples productos
- ✅ Descuento automático de stock (transacciones atómicas)
- ✅ Validación de stock antes de vender
- ✅ Cálculo automático de impuestos y totales
- ✅ Facturación electrónica opcional (CAE)
- ✅ Cancelación de ventas con reversión de stock
- ✅ Filtros avanzados (cliente, fecha, método de pago)
- ✅ Control de permisos por rol

#### 💵 **Cash Count / Cierre de Caja**
- ✅ Registro de apertura/cierre por usuario y turno
- ✅ Conciliación de efectivo contado vs. sistema
- ✅ Registro de diferencias (sobrante/faltante) con observaciones

#### 📊 **Analytics**
- ✅ Paneles y métricas clave de ventas e inventario
- ✅ Filtros por rango de fechas, usuario y punto de venta
- ✅ KPIs para seguimiento de rendimiento

#### 🤖 **IA**
- ✅ Endpoints y servicios de soporte para automatizaciones IA
- ✅ Preparado para integración con proveedores (OpenAI/Anthropic/Ollama)

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest neos_core/tests -v

# Ejecutar tests con coverage
pytest neos_core/tests -v --cov=neos_core --cov-report=html

# Ejecutar solo tests de ventas
pytest neos_core/tests/test_sales.py -v

# Ver reporte de coverage
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html  # Windows
```

**Coverage actual:** ~95% ✅

---

## 🔐 Seguridad

- 🔒 **JWT con expiración** (30 minutos por defecto)
- 🔒 **Hashing de contraseñas** con bcrypt
- 🔒 **Validación estricta** con Pydantic
- 🔒 **Aislamiento multi-tenant** en todas las operaciones
- 🔒 **Protección contra inyección SQL** (ORM)
- 🔒 **CORS configurado** para producción

---

## 📋 Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | URL de conexión a PostgreSQL | `postgresql://user:pass@localhost:5434/neos_db` |
| `SECRET_KEY` | Clave para firmar JWT (generar con `openssl rand -hex 32`) | `abc123...` |
| `ALGORITHM` | Algoritmo de firma JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tiempo de vida del token | `30` |

---

## 🛣️ Roadmap

### ✅ Fase 1: Core y Ventas (COMPLETADO)
- ✅ Multi-tenancy y autenticación
- ✅ Gestión de usuarios y roles
- ✅ Inventario con stock
- ✅ Módulo de ventas completo

### 🚧 Fase 2: Funcionalidades Avanzadas (En Progreso)
- [ ] Actualización (PUT/PATCH) de entidades
- [ ] Soft delete de productos y clientes
- [ ] Dashboard con métricas
- [ ] Endpoint `/users/me`

### 📅 Fase 3: Módulo Contable (Futuro)
- [ ] Asientos contables automáticos
- [ ] Estado de resultados
- [ ] Balance
- [ ] Clasificador de gastos con IA

### 📅 Fase 4: Inteligencia Artificial (Futuro)
- [ ] Catalogador de productos con visión
- [ ] Búsqueda semántica en POS
- [ ] Predicción de demanda
- [ ] Chat con datos (NLP to SQL)

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 👥 Equipo

Desarrollado con ❤️ por el equipo **Neos**

---

## 📞 Soporte

- **Issues:** [GitHub Issues](https://github.com/tu-usuario/Neos-Core/issues)
- **Documentación:** [Wiki del Proyecto](https://github.com/tu-usuario/Neos-Core/wiki)
- **Email:** soporte@neos.com
