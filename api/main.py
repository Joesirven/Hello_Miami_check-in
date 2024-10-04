# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.routers import contacts, interactions, messages, blasts
from api.lifespan import lifespan
from api.db.database import db
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
import logging


load_dotenv()

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Twilio SMS API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
app.include_router(interactions.router,
                   prefix="/interactions",
                   tags=["interactions"])
app.include_router(messages.router,
                   prefix="/messages",
                   tags=["messages"])
app.include_router(blasts.router,
                   prefix="/blasts",
                   tags=["blasts"])


@app.get("/")
async def root(session: AsyncSession = Depends(db.get_db)):
    result = await db.test_connection()
    return {"message": "Welcome to the Twilio SMS API", "result": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
