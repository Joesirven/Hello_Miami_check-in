from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from api.schemas import Message, MessageCreate
from api.db.database import db
from api.queries import interactions as interaction_queries
from api.utils.twilio_helpers import send_sms_and_update_interaction
from api.queries import messages

router = APIRouter()


@router.post("/", response_model=Message)
def create_message(
    message: MessageCreate,
    db: Session = Depends(db.get_db)
):
    return messages.create_message(db=db, message=message)


@router.get("/", response_model=list[Message])
def read_messages(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(db.get_db)
):
    return messages.get_messages(db, skip=skip, limit=limit)


@router.get("/{message_id}", response_model=Message)
def read_message(message_id: int, db: Session = Depends(db.get_db)):
    db_message = messages.get_message(db, message_id=message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return db_message


@router.put("/{message_id}", response_model=Message)
def update_message(
    message_id: int,
    message: MessageCreate,
    db: Session = Depends(db.get_db)
):
    db_message = messages.update_message(
        db,
        message_id=message_id,
        message=message
        )
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return db_message


@router.delete("/{message_id}", response_model=Message)
def delete_message(message_id: int, db: Session = Depends(db.get_db)):
    db_message = messages.delete_message(db, message_id=message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return db_message


@router.post("/send", response_model=MessageCreate)
async def send_message(
    message: MessageCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(db.get_db)
):
    # Fetch the contact
    message = db.query(Message)
    filtered_contact = message.filter(
        Message.id == message.message_id
        ).first()

    if not filtered_contact:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
            )

    # Create the interaction first
    db_interaction = interaction_queries.create_interaction(
        db=db,
        interaction=message
        )

    # Add the SMS sending task to background tasks
    background_tasks.add_task(
        send_sms_and_update_interaction,
        filtered_contact.phone_number,
        message.message,
        db_interaction.id,
        db
    )

    return db_interaction


@router.get("/schedule", response_model=Message)
async def get_scheduled_messages(db: Session = Depends(db.get_db)):
    # This endpoint is intended to retrieve scheduled messages
    # However, it's currently incomplete and lacks implementation
    # TODO: Implement logic to fetch and return scheduled messages
    raise HTTPException(status_code=501, detail="Not implemented")
