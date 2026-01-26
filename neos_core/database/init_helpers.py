import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url

from neos_core.database.config import Base, SessionLocal, engine
from neos_core.database.seed import run_full_seed


def _get_database_url(logger):
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    from neos_core.database.config import DATABASE_URL

    logger.warning("DATABASE_URL not found in .env; falling back to config.py value.")
    return DATABASE_URL


def ensure_database_exists(logger):
    database_url = _get_database_url(logger)
    try:
        url = make_url(database_url)
    except Exception as exc:
        logger.error(f"Invalid DATABASE_URL: {exc}")
        return False

    if not url.database:
        logger.error("DATABASE_URL does not include a database name.")
        return False

    if not url.drivername.startswith("postgresql"):
        logger.warning("Non-PostgreSQL database detected; skipping database existence check.")
        return True

    server_url = url.set(database="postgres")
    db_name = url.database

    logger.step("Checking if target database exists...")
    server_engine = create_engine(server_url, isolation_level="AUTOCOMMIT")
    try:
        with server_engine.connect() as conn:
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": db_name},
            ).first()
            if result:
                logger.success(f"Database '{db_name}' already exists.")
                return True

            safe_db_name = db_name.replace('"', '""')
            logger.step(f"Database '{db_name}' not found. Creating...")
            conn.execute(text(f'CREATE DATABASE "{safe_db_name}"'))
            logger.success(f"Database '{db_name}' created.")
            return True
    except Exception as exc:
        logger.error(f"Error checking/creating database: {exc}")
        return False
    finally:
        server_engine.dispose()


def drop_all_tables(logger):
    """Drop all tables using SQLAlchemy metadata."""
    logger.step("Dropping all existing tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        logger.success("All tables dropped")
        return True
    except Exception as exc:
        logger.error(f"Error dropping tables: {exc}")
        return False


def create_all_tables(logger):
    """Create all tables using SQLAlchemy metadata."""
    logger.step("Creating all tables...")
    try:
        if not ensure_database_exists(logger):
            return False, 0

        Base.metadata.create_all(bind=engine)

        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        logger.success(f"{len(tables)} tables created:")
        for table in sorted(tables):
            logger.info(f"    - {table}")

        return True, len(tables)
    except Exception as exc:
        logger.error(f"Error creating tables: {exc}")
        import traceback

        traceback.print_exc()
        return False, 0


def load_initial_data(logger):
    """Load seed data."""
    logger.step("Loading initial data (seed)...")
    try:
        db = SessionLocal()
        try:
            run_full_seed(db)
            logger.success("Initial data loaded")
            return True
        finally:
            db.close()
    except Exception as exc:
        logger.error(f"Error loading initial data: {exc}")
        import traceback

        traceback.print_exc()
        return False
