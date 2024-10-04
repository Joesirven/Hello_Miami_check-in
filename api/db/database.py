import os
import logging
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncConnection,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from dotenv import load_dotenv
import asyncio
from typing import AsyncGenerator
from contextlib import asynccontextmanager
import ssl


load_dotenv()

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Create a Base class for declarative models
Base = declarative_base()

# Get database credentials from environment variables
PASSWORD = os.environ.get("SUPABASE_PASSWORD")
SSL_CERT = os.environ.get("SSL_CERT")

ssl_context = ssl.create_default_context(cafile=SSL_CERT)
ssl_context.verify_mode = ssl.CERT_REQUIRED


# Connection string with SSL
connection_string = (
    f"postgresql+asyncpg://postgres.aiqeerqjrikfckozfygt:{PASSWORD}"
    "@aws-0-us-east-1.pooler.supabase.com:5432/postgres"
)

logger.info(f"Connection string: {connection_string}")

# Create the async engine with SSL
async_engine_ssl = create_async_engine(
    connection_string,
    echo=True,
    connect_args={
        "ssl": ssl_context
    }
)


class AsyncDatabaseSession:
    def __init__(self, engine: AsyncConnection):
        self._engine: AsyncConnection = engine
        self._session: AsyncSession = None

    async def init(self) -> None:
        try:
            self._session = sessionmaker(
                bind=self._engine, expire_on_commit=False, class_=AsyncSession
            )()
            logger.info("Database connection initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database connection: {str(e)}")
            raise

    async def create_all(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("All database tables created")
            await conn.commit()

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        if not self._session:
            await self.init()
        try:
            yield self._session
            await self._session.commit()
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise e
        finally:
            await self._session.close()

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[AsyncConnection, None]:
        async with self._engine.connect() as conn:
            logger.info("Using connection from engine")
            yield conn

    async def test_connection(self) -> bool:
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                async with self.get_connection() as conn:
                    result = await conn.execute(text("SELECT 1"))
                    logger.info(f"Database connection test passed: {result}")
                return True
            except SQLAlchemyError as e:
                logger.error(f"Database connection test failed"
                             f"(attempt {attempt + 1}): {str(e)}"
                             )
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    return False


# Create an instance of the AsyncDatabaseSession class with SSL
db = AsyncDatabaseSession(async_engine_ssl)


# async def main():
#     await db.init()
#     result = await db.test_connection()
#     print(result)

# if __name__ == "__main__":
#     asyncio.run(main())
