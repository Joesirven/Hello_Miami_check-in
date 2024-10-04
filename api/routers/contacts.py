# routers/contacts.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import api.schemas as schemas
import api.models as models
from api.db.database import db
import logging
from typing import List
from sqlalchemy import select


router = APIRouter()


@router.post("/", response_model=schemas.Contact)
async def create_contact(
    contact: schemas.ContactCreate,
    db: AsyncSession = Depends(db.get_db)
):
    logger = logging.getLogger(__name__)
    logger.info(f"Attempting to create contact: {contact}")
    try:
        db_contact = models.Contact(**contact.model_dump())
        db.add(db_contact)
        await db.flush()  # This will generate the contact_id

        logger.debug(f"Contact flushed with ID: {db_contact.contact_id}")

        # At this point, db_contact.contact_id should be available

        # Perform any additional operations if needed

        await db.commit()  # Commit the transaction
        logger.info(f"Contact created successfully: {db_contact}")

        return db_contact
    except Exception as e:
        await db.rollback()  # Rollback in case of any exception
        logger.error(f"Error creating contact: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await db.close()  # Ensure the session is closed
        logger.debug("Database session closed")


@router.get("/", response_model=List[schemas.Contact])
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(db.get_db)
        ) -> List[schemas.Contact]:
    query = select(models.Contact).offset(skip).limit(limit)
    result = await db.execute(query)
    contacts = result.scalars().all()
    return contacts


@router.get("/{contact_id}", response_model=schemas.Contact)
async def read_contact(contact_id: int, db: AsyncSession = Depends(db.get_db)):
    query = select(models.Contact).filter(
        models.Contact.contact_id == contact_id
        )
    result = await db.execute(query)
    db_contact = result.scalar()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.put("/{contact_id}", response_model=schemas.Contact)
async def update_contact(
    contact_id: int,
    contact: schemas.ContactUpdate,
    db: AsyncSession = Depends(db.get_db)
        ) -> schemas.Contact:
    query = select(models.Contact).filter(
        models.Contact.contact_id == contact_id
        )
    result = await db.execute(query)
    db_contact = result.scalar()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    for var, value in vars(contact).items():
        setattr(db_contact, var, value) if value else None
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact


@router.delete("/{contact_id}", response_model=schemas.Contact)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(db.get_db)
        ) -> schemas.Contact:
    query = select(models.Contact).filter(
        models.Contact.contact_id == contact_id
        )
    result = await db.execute(query)
    db_contact = result.scalar()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    await db.delete(db_contact)
    await db.commit()
    return db_contact
