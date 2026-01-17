#!/usr/bin/env python3
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from neos_core.database.config import Base, SessionLocal, engine
from neos_core.database.models import *
from neos_core.database.seed import run_full_seed


class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


def print_header(message):
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}{message.center(60)}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print()


def print_step(message):
    print(f"{Colors.BLUE}> {message}{Colors.NC}")


def print_success(message):
    print(f"{Colors.GREEN}[OK] {message}{Colors.NC}")


def print_error(message):
    print(f"{Colors.RED}[ERROR] {message}{Colors.NC}")


def print_warning(message):
    print(f"{Colors.YELLOW}[WARNING] {message}{Colors.NC}")


def drop_all_tables():
    """Drop all tables using SQLAlchemy metadata"""
    print_step("Dropping all existing tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print_success("All tables dropped")
        return True
    except Exception as e:
        print_error(f"Error dropping tables: {e}")
        return False


def create_all_tables():
    """Create all tables using SQLAlchemy metadata"""
    print_step("Creating all tables...")
    try:
        Base.metadata.create_all(bind=engine)

        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print_success(f"{len(tables)} tables created:")
        for table in sorted(tables):
            print(f"    - {table}")

        return True, len(tables)
    except Exception as e:
        print_error(f"Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False, 0


def load_initial_data():
    """Load seed data"""
    print_step("Loading initial data (seed)...")
    try:
        db = SessionLocal()
        try:
            run_full_seed(db)
            print_success("Initial data loaded")
            return True
        finally:
            db.close()
    except Exception as e:
        print_error(f"Error loading initial data: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print_header("NEOS-CORE: Database Initialization")

    load_dotenv()

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print_error("DATABASE_URL not found in .env")
        print("Create .env file with:")
        print("DATABASE_URL=postgresql://user:password@localhost:5432/neos_db")
        sys.exit(1)

    print_success("DATABASE_URL loaded")

    try:
        db_name = database_url.split('/')[-1].split('?')[0]
        print(f"  - Database: {db_name}")
    except:
        print_warning("Could not parse database name from URL")

    print()

    print_warning("WARNING:")
    print("  - ALL existing tables will be DELETED")
    print("  - All data will be LOST")
    print("  - Tables will be recreated from scratch")
    print("  - Initial seed data will be loaded")
    print()

    confirm = input("Continue? (type 'YES' in uppercase): ")

    if confirm != "YES":
        print_error("Operation cancelled")
        sys.exit(0)

    print()

    # Step 1: Drop all tables
    if not drop_all_tables():
        sys.exit(1)

    print()

    # Step 2: Create all tables
    success, table_count = create_all_tables()
    if not success:
        sys.exit(1)

    print()

    # Step 3: Load seed data
    if not load_initial_data():
        sys.exit(1)

    print()

    # Success summary
    print(f"{Colors.GREEN}{'=' * 60}{Colors.NC}")
    print(f"{Colors.GREEN}SUCCESS: Database initialized successfully{Colors.NC}")
    print(f"{Colors.GREEN}{'=' * 60}{Colors.NC}")
    print()

    print(f"{Colors.BLUE}System status:{Colors.NC}")
    print(f"  - Database: {db_name}")
    print(f"  - Tables: {table_count} created")
    print(f"  - Initial data: Loaded")
    print()

    print(f"{Colors.BLUE}Next steps:{Colors.NC}")
    print(f"  1. Start server:")
    print(f"     {Colors.GREEN}python -m uvicorn main:app --reload{Colors.NC}")
    print()
    print(f"  2. View API docs:")
    print(f"     {Colors.GREEN}http://localhost:8000/docs{Colors.NC}")
    print()
    print(f"  3. Run tests:")
    print(f"     {Colors.GREEN}pytest tests/ -v{Colors.NC}")
    print()

    print(f"{Colors.YELLOW}Tips:{Colors.NC}")
    print("  - Check seed data in: neos_core/database/seed.py")
    print("  - Verify tables in DBeaver")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_warning("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print()
        print_error(f"Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)