# init_system.py
from neos_core.database.config import SessionLocal
from neos_core.database.models import User, Tenant, Role
from neos_core import crud, schemas

def initialize_neos():
    db = SessionLocal()
    try:
        # 1. Verificar si ya existe el SuperAdmin para evitar ejecuciones múltiples
        existing_admin = db.query(User).filter(User.email == "admin@neos.com").first()
        if existing_admin:
            print("⚠️ El sistema ya ha sido inicializado anteriormente.")
            return

        print("🚀 Iniciando creación de administrador maestro...")

        # 2. Crear el Tenant Maestro (Neos Core)
        tenant_in = schemas.TenantCreate(
            name="Neos Core HQ",
            description="Administración Central del SaaS"
        )
        tenant = crud.create_tenant(db, tenant_in)
        print(f"✅ Tenant Maestro creado (ID: {tenant.id})")

        # 3. Crear el SuperAdmin vinculado al rol 1
        # IMPORTANTE: Asegúrate de que el seeder de roles ya se ejecutó
        user_in = schemas.UserCreate(
            email="admin@neos.com",
            password="adminpassword123", # Cambia esto tras la primera entrada
            full_name="Super Administrador Neos",
            tenant_id=tenant.id,
            role_id=1, # Role ID 1 = superadmin
            is_active=True
        )
        user = crud.create_user(db, user_in)
        print(f"✅ SuperAdmin creado: {user.email}")
        print("\n✨ Sistema listo para pruebas. Ya puedes borrar este script.")

    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    initialize_neos()