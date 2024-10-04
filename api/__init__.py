# api/__init__.py
from . import routers
import logging

logger = logging.getLogger(__name__)


try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Environment variables loaded from .env file")
except ImportError:
    logger.warning("python-dotenv not found. Ensure environment variables are set manually.")
