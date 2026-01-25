from neos_core.database.config import Base, SessionLocal, engine
from neos_core.database.seed import run_full_seed


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
