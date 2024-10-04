from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from api.schemas import Interaction, InteractionCreate
from api.db.database import db
from api.queries import interactions as interaction_queries
from api.queries import contacts as contact_queries
from api.utils.twilio_helpers import send_sms_and_update_interaction

router = APIRouter()


@router.post("/send", response_model=Interaction)
async def send_message(
    message: InteractionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(db.get_db)
):
    # Fetch the contact
    contact = contact_queries.get_contact(
        db,
        contact_id=message.contact_id
        )

    if not contact:
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
        contact.phone_number,
        message.message,
        db_interaction.interaction_id,
        db
    )

    return db_interaction
