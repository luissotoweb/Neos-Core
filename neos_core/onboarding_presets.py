"""Presets de onboarding por rubro para la configuración inicial."""

PRESET_DEFINITIONS = {
    "retail": {
        "categories": ["ventas", "inventario", "clientes"],
        "active_modules": ["sales", "products", "clients"],
    },
    "servicios": {
        "categories": ["servicios", "facturacion", "clientes"],
        "active_modules": ["sales", "clients"],
    },
}
