# NEXUS PyME

## Visión
Sistema de gestión integral (ERP/POS) agnóstico, modular y potenciado por IA, diseñado para funcionar tanto en una ferretería técnica como en un supermercado de alta rotación, automatizando la contabilidad y la toma de decisiones.

## 1. Stack Tecnológico y Arquitectura

### Backend (El Cerebro)
- Lenguaje: Python 3.10+
- Framework: FastAPI (por velocidad, tipado estricto y soporte asíncrono)
- ORM: SQLAlchemy (gestión de base de datos) + Pydantic (validación de datos)
- IA Integration: OpenAI API / Anthropic (vía librerías oficiales de Python) u Ollama (local)

### Frontend (La Cara)
- Framework: React.js (Vite)
- Estilos: Tailwind CSS (diseño rápido y responsivo)
- Estado: Zustand o Redux Toolkit
- Offline: Service Workers (PWA) para funcionamiento sin internet

### Base de Datos (La Memoria)
- Motor: PostgreSQL
- Estrategia clave: uso de columnas JSONB para atributos flexibles de productos (permite que un producto tenga "Talla" y otro "Voltaje" en la misma tabla)

## 2. Módulos del Sistema (Desglose Funcional)

### MÓDULO 0: NÚCLEO Y MULTI-TENANCY
La base para que el sistema sea seguro y escalable.

- [REQ-0.1] Arquitectura multi-empresa: el sistema debe soportar múltiples empresas (tenants) en la misma base de datos, separando la información lógicamente.
- [REQ-0.2] Autenticación segura: login mediante JWT (JSON Web Tokens). Roles definidos: Admin, Cajero, Gerente, Contador.
- [REQ-0.3] Onboarding inteligente: al crear una empresa, el usuario selecciona el rubro (Ej: Ferretería). El sistema pre-configura categorías y desactiva módulos innecesarios.

### MÓDULO 1: INVENTARIO POLIMÓRFICO
Gestión de productos adaptable a cualquier rubro.

- [REQ-1.1] Ficha de producto flexible:
  - Campos fijos: SKU, Nombre, Costo, Precio, Stock, Código de Barras.
  - Campos dinámicos (JSONB): atributos custom (Talla, Color, Material, Vencimiento).
- [REQ-1.2] Unidades de medida duales: capacidad de definir "Unidad de Compra" (Caja de 50) y "Unidad de Venta" (Unidad suelta). El sistema convierte automáticamente al vender.
- [REQ-1.3] Tipos de producto: soporte para:
  - Simple: (Lata de atún).
  - Kit/Combo: (Pack Parrillero: Carbón + Carne). Descuenta los componentes individuales.
  - Servicio: (Mano de obra). No mueve stock.
- [REQ-1.4] IA catalogador (visión): subir foto de etiqueta -> IA extrae datos -> formulario se llena solo.

### MÓDULO 2: PUNTO DE VENTA (POS)
Interfaz de venta rápida y sin fricción.

- [REQ-2.1] Buscador híbrido:
  - Escáner (input exacto de código de barras).
  - Búsqueda semántica (IA): el cajero escribe "Tubo agua caliente" y el sistema sugiere "Tubo PPR 20mm".
- [REQ-2.2] Carrito y "Venta en Espera": posibilidad de pausar una venta para atender a otro cliente y recuperarla después.
- [REQ-2.3] Cierre de caja ciego: el cajero ingresa el efectivo contado. El sistema compara contra lo registrado y reporta diferencias (Sobrante/Faltante).
- [REQ-2.4] Modo offline: si cae internet, las ventas se guardan en el navegador (Local Storage) y se sincronizan al volver la conexión.

### MÓDULO 3: AUTOCONTABILIDAD (EL CONTADOR INVISIBLE)
Conversión automática de operaciones a contabilidad.

- [REQ-3.1] Motor de asientos automáticos: cada vez que se confirma una venta o compra, el sistema genera registros en el libro diario (Debe/Haber) sin intervención humana.
- [REQ-3.2] Gestión de impuestos: configuración de tasas de IVA/Tax. El motor contable separa el Neto del Impuesto en cuentas pasivas automáticamente.
- [REQ-3.3] Borrador fiscal (draft mode):
  - Dashboard que permite seleccionar un rango de fechas.
  - Muestra una previsualización del estado de resultados y balance.
  - Permite editar asientos manuales antes de "Cerrar el Periodo".
- [REQ-3.4] Clasificador de gastos (IA): al subir un gasto manual (Ej: "Uber"), la IA sugiere la cuenta contable (Ej: "Gastos de Movilidad").

### MÓDULO 4: INTELIGENCIA Y DASHBOARDS
Toma de decisiones basada en datos.

- [REQ-4.1] Chat con tus datos (NLP to SQL): interfaz de chat donde el dueño pregunta "¿Qué vendí más el viernes pasado?" y el sistema responde con el dato exacto.
- [REQ-4.2] Predicción de demanda simple: análisis del histórico de ventas para sugerir la "Orden de Compra Ideal" y evitar quiebres de stock.
- [REQ-4.3] Dashboard de anomalías: alertas automáticas: "El producto X tiene margen negativo hoy" o "El inventario de Y no cuadra".

## 3. Hoja de Ruta de Desarrollo (Roadmap MVP)

### FASE 1: El Esqueleto (Semanas 1-3)
- Backend: setup de FastAPI, conexión a DB, modelos de usuario y producto (con JSONB).
- Frontend: login, CRUD de productos (crear y listar).
- Hito: puedes loguearte y crear un producto con atributos dinámicos.

### FASE 2: La Caja (Semanas 4-6)
- Backend: endpoints de venta (transaction atomic).
- Frontend: interfaz de POS, carrito, buscador, ticket de venta.
- Hito: puedes realizar una venta completa y se descuenta del inventario.

### FASE 3: El Contador (Semanas 7-9)
- Backend: tablas contables (asientos/cuentas). Triggers que se activan al vender (módulo de autocontabilidad).
- Frontend: reporte de ventas del día y borrador fiscal preliminar.
- Hito: vendes un producto y ves cómo aparece mágicamente en el reporte de ganancias.

### FASE 4: El Cerebro IA (Semanas 10+)
- Integración: conectar OpenAI API.
- Features: implementar el catalogador por foto y el chat de datos.
- Hito: el sistema se vuelve "inteligente".

## 4. Estructura de Base de Datos Sugerida (Entidades Clave)

Tablas principales en PostgreSQL:

- tenants: (id, nombre_empresa, plan)
- users: (id, tenant_id, email, password_hash, role)
- products: (id, tenant_id, sku, name, price, cost, attributes [JSONB], stock)
- sales: (id, tenant_id, total, date, user_id, payment_method)
- sale_items: (id, sale_id, product_id, qty, unit_price)
- accounting_moves: (id, tenant_id, date, concept, is_draft)
- accounting_lines: (id, move_id, account_id, debit, credit)
