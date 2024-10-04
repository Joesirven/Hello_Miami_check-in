import asyncio
from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from api.db.database import db
import logging
from alembic.migration import MigrationContext

logger = logging.getLogger(__name__)


async def run_migrations():
    logger.info("Starting migration process")
    alembic_cfg = Config("api/alembic.ini")
    try:
        async with db.get_connection() as connection:
            logger.info("Got database connection")
            await connection.run_sync(
                lambda conn: command.upgrade(alembic_cfg, "head")
            )
        logger.info("Migrations completed successfully")
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise


async def check_migrations():
    try:
        alembic_cfg = Config("api/alembic.ini")
        alembic_cfg.set_main_option("script_location", "api/alembic")
        script = ScriptDirectory.from_config(alembic_cfg)

        async with db.get_connection() as connection:
            def get_current_revision(connection):
                context = MigrationContext.configure(connection)
                return context.get_current_revision()

            current_rev = await connection.run_sync(get_current_revision)
            head_rev = script.get_current_head()

        if current_rev != head_rev:
            logger.warning(
                f"Pending migrations detected. "
                f"Current: {current_rev}, Latest: {head_rev}"
            )
            return False
        else:
            logger.info("No pending migrations")
            return True
    except Exception as e:
        logger.error(f"Error checking migrations: {str(e)}")
        return False


async def async_main():
    await db.init()
    await run_migrations()


if __name__ == "__main__":
    asyncio.run(async_main())
