import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from api.db.database import async_engine_ssl, db
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from api.migrations import check_migrations, run_migrations

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting application lifespan")

    try:
        # Initialize the database session
        await db.init()
        logger.info("Database session initialized")

        # Test the database connection
        try:
            async with db.get_connection() as conn:
                result = await conn.execute(text("SELECT 1"))
                logger.info(
                    "Database connection test successful: %s",
                    result.fetchone(),
                )
        except SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {str(e)}")
            raise

        # Check for pending migrations and run them
        migrations_up_to_date = await check_migrations()
        if not migrations_up_to_date:
            logger.warning(
                "Pending migrations detected."
                "Running migrations..."
            )
            await run_migrations()
        else:
            logger.info("Database schema is up to date")

        yield

    except Exception as e:
        logger.error(f"An error occurred during application startup: {str(e)}")
        raise

    finally:
        # Cleanup: dispose of the database engine
        await async_engine_ssl.dispose()
        logger.info("Database engine disposed")


# async def test_database_connection():
#     try:
#         await db.init()
#         async with db.get_connection() as conn:
#             result = await conn.execute(text("SELECT 1"))
#             print(f"Database connection test"
# result: {await result.fetchone()}")
#     except Exception as e:
#         print(f"Database connection test failed: {str(e)}")
#     finally:
#         await async_engine_ssl.dispose()

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(test_database_connection())
