from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.schemas import Blast, BlastCreate
from api.queries import blasts
from api.db.database import db

router = APIRouter()

blast_manager = blasts.BlastManager(db)


@router.post("/", response_model=Blast)
async def create_blast(
    blast: BlastCreate,
    db: Session = Depends(db.get_db)
):
    return await blast_manager.create_blast(blast)


@router.get("/{blast_id}", response_model=Blast)
async def read_blast(
    blast_id: int,
    db: Session = Depends(db.get_db)
):
    db_blast = await blast_manager.get_blast(blast_id)
    if db_blast is None:
        raise HTTPException(status_code=404, detail="Blast not found")
    return db_blast


@router.get("/", response_model=list[Blast])
async def read_blasts(
    db: Session = Depends(db.get_db)
):
    db_blast = await blast_manager.get_blasts()
    if db_blast is None:
        raise HTTPException(status_code=404, detail="Blast not found")
    return db_blast


@router.put("/{blast_id}", response_model=Blast)
async def update_blast(
    blast_id: int,
    blast: BlastCreate,
    db: Session = Depends(db.get_db)
):
    db_blast = await blast_manager.update_blast(blast_id, blast)
    if db_blast is None:
        raise HTTPException(status_code=404, detail="Blast not found")
    return db_blast


@router.post("/{blast_id}/send", response_model=Blast)
async def send_blast(
    blast_id: int,
    db: Session = Depends(db.get_db)
):
    db_blast = await blast_manager.send_blast(blast_id)
    if db_blast is None:
        raise HTTPException(status_code=404, detail="Blast not found")
    return db_blast
