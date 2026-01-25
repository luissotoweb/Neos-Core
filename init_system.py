#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from neos_core import crud, schemas
from neos_core.database.config import SessionLocal
from neos_core.database.init_helpers import (
    create_all_tables,
    drop_all_tables,
    load_initial_data,
)
from neos_core.database.models import User


class InitLogger:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

    def header(self, message):
        print(f"{self.BLUE}{'=' * 60}{self.NC}")
        print(f"{self.BLUE}{message.center(60)}{self.NC}")
        print(f"{self.BLUE}{'=' * 60}{self.NC}")
        print()

    def step(self, message):
        print(f"{self.BLUE}> {message}{self.NC}")

    def success(self, message):
        print(f"{self.GREEN}[OK] {message}{self.NC}")

    def error(self, message):
        print(f"{self.RED}[ERROR] {message}{self.NC}")

    def warning(self, message):
        print(f"{self.YELLOW}[WARNING] {message}{self.NC}")

    def info(self, message):
        print(message)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Initialize Neos-Core system with database reset, seed, and admin creation."
    )
    parser.add_argument(
        "--skip-drop-create",
        action="store_true",
        help="Skip dropping and creating tables (keep existing schema).",
    )
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="Skip confirmation prompt for destructive actions.",
    )
    return parser.parse_args()


def create_tenant_and_admin(logger):
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.email == "admin@neos.com").first()
        if existing_admin:
            logger.warning("El SuperAdmin ya existe. Se omite la creación.")
            return True

        logger.step("Creando tenant maestro y SuperAdmin...")
        tenant_in = schemas.TenantCreate(
            name="Neos Core HQ",
            description="Administración Central del SaaS",
        )
        tenant = crud.create_tenant(db, tenant_in)
        logger.success(f"Tenant Maestro creado (ID: {tenant.id})")

        user_in = schemas.UserCreate(
            email="admin@neos.com",
            password="adminpassword123",
            full_name="Super Administrador Neos",
            tenant_id=tenant.id,
            role_id=1,
            is_active=True,
        )
        user = crud.create_user(db, user_in)
        logger.success(f"SuperAdmin creado: {user.email}")
        return True
    except Exception as exc:
        logger.error(f"Error durante la creación de tenant/admin: {exc}")
        return False
    finally:
        db.close()


def validate_env(logger):
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not found in .env")
        logger.info("Create .env file with:")
        logger.info("DATABASE_URL=postgresql://user:password@localhost:5432/neos_db")
        return None

    logger.success("DATABASE_URL loaded")
    try:
        db_name = database_url.split("/")[-1].split("?")[0]
        logger.info(f"  - Database: {db_name}")
    except Exception:
        db_name = None
        logger.warning("Could not parse database name from URL")

    return db_name


def main():
    logger = InitLogger()
    args = parse_args()

    logger.header("NEOS-CORE: System Initialization")

    db_name = validate_env(logger)
    if not db_name:
        sys.exit(1)

    logger.info("")

    if not args.skip_drop_create:
        logger.warning("WARNING:")
        logger.info("  - ALL existing tables will be DELETED")
        logger.info("  - All data will be LOST")
        logger.info("  - Tables will be recreated from scratch")
        logger.info("  - Initial seed data will be loaded")
        logger.info("")

        if not args.no_confirm:
            confirm = input("Continue? (type 'YES' in uppercase): ")
            if confirm != "YES":
                logger.error("Operation cancelled")
                sys.exit(0)

        logger.info("")

        if not drop_all_tables(logger):
            sys.exit(1)

        logger.info("")

        success, table_count = create_all_tables(logger)
        if not success:
            sys.exit(1)
    else:
        table_count = None

    logger.info("")

    if not load_initial_data(logger):
        sys.exit(1)

    logger.info("")

    if not create_tenant_and_admin(logger):
        sys.exit(1)

    logger.info("")

    logger.info(f"{logger.GREEN}{'=' * 60}{logger.NC}")
    logger.info(f"{logger.GREEN}SUCCESS: System initialized successfully{logger.NC}")
    logger.info(f"{logger.GREEN}{'=' * 60}{logger.NC}")
    logger.info("")

    logger.info(f"{logger.BLUE}System status:{logger.NC}")
    logger.info(f"  - Database: {db_name}")
    if table_count is not None:
        logger.info(f"  - Tables: {table_count} created")
    else:
        logger.info("  - Tables: existing schema kept")
    logger.info("  - Initial data: Loaded")
    logger.info("  - Admin: Ensured")
    logger.info("")

    logger.info(f"{logger.BLUE}Next steps:{logger.NC}")
    logger.info("  1. Start server:")
    logger.info(f"     {logger.GREEN}python -m uvicorn main:app --reload{logger.NC}")
    logger.info("")
    logger.info("  2. View API docs:")
    logger.info(f"     {logger.GREEN}http://localhost:8000/docs{logger.NC}")
    logger.info("")
    logger.info("  3. Run tests:")
    logger.info(f"     {logger.GREEN}pytest tests/ -v{logger.NC}")
    logger.info("")

    logger.info(f"{logger.YELLOW}Tips:{logger.NC}")
    logger.info("  - Check seed data in: neos_core/database/seed.py")
    logger.info("  - Verify tables in DBeaver")
    logger.info("")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        InitLogger().warning("Operation cancelled by user")
        sys.exit(0)
    except Exception as exc:
        print()
        InitLogger().error(f"Unexpected error: {exc}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
