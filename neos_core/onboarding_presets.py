"""Presets de onboarding por rubro para la configuración inicial."""

PRESET_DEFINITIONS = {
    "retail": {
        "categories": ["ventas", "inventario", "clientes"],
        "active_modules": ["sales", "products", "clients"],
    },
    "ferreteria": {
        "categories": ["herramientas", "materiales", "inventario", "clientes", "proveedores", "ventas"],
        "active_modules": ["sales", "products", "inventory", "clients", "suppliers", "purchases"],
    },
    "supermercado": {
        "categories": ["alimentos", "bebidas", "limpieza", "caja", "inventario", "clientes"],
        "active_modules": ["sales", "products", "inventory", "clients", "cash"],
    },
    "restaurante": {
        "categories": ["menu", "insumos", "reservas", "clientes", "ventas"],
        "active_modules": ["sales", "products", "inventory", "clients", "tables"],
    },
    "farmacia": {
        "categories": ["medicamentos", "recetas", "inventario", "clientes", "ventas"],
        "active_modules": ["sales", "products", "inventory", "clients"],
    },
    "panaderia": {
        "categories": ["panificados", "pasteleria", "insumos", "ventas", "clientes"],
        "active_modules": ["sales", "products", "inventory", "clients"],
    },
    "servicios": {
        "categories": ["servicios", "facturacion", "clientes"],
        "active_modules": ["sales", "clients"],
    },
}
