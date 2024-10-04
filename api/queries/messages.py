from sqlalchemy.orm import Session
import api.models as models
import api.schemas as schemas
from api.utils.twilio_helpers import send_sms
from api.utils.mailersend_helpers import HTMLEmail, SimpleEmail
from datetime import datetime


def create_message(
        db: Session,
        message: schemas.MessageCreate,
        sender: str,
        send_time: datetime,
        ):
    db_message = models.Message(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    if db_message.type == models.MessageType.SMS:
        send_sms(
            db_message.contact.phone_number,
            db_message.content,
            db_message.scheduled_time
            )
    elif db_message.type == models.MessageType.EMAIL:
        if db_message.html_content:
            email = HTMLEmail()
            email.set_content(db_message.html_content, db_message.content)
        else:
            email = SimpleEmail()
            email.set_content(db_message.content)
        sender_name = sender or "hello_miami"
        sender_email = "nerd@hellomiami.org"
        email.set_sender(sender_name, sender_email)
        email.set_recipients([{"email": db_message.contact.email}])
        email.set_subject(db_message.subject)
        email.set_send_at(send_time)
        response = email.send()

    return response


def get_messages(
        db: Session,
        skip: int = 0,
        limit: int = 100
        ):
    return db.query(models.Message).offset(skip).limit(limit).all()


def get_message(db: Session, message_id: int):
    return db.query(
        models.Message
        ).filter(
            models.Message.message_id == message_id
            ).first()


def update_message(
        db: Session,
        message_id: int,
        message: schemas.MessageCreate
        ):
    db_message = get_message(db, message_id)
    if db_message:
        for key, value in message.dict(exclude_unset=True).items():
            setattr(db_message, key, value)
        db.commit()
        db.refresh(db_message)
    return db_message


def delete_message(db: Session, message_id: int):
    db_message = get_message(db, message_id)
    if db_message:
        db.delete(db_message)
        db.commit()
    return db_message

# Add similar functions for Blast model
