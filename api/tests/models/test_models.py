import pytest
from sqlalchemy.orm import Session
from api.models import (
    Blast,
    Contact,
    Message,
    Interaction,
    BlastRecipient,
    MessageType,
    MessageDirection,
    Status
)
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def test_contact_model(db: Session):
    contact = Contact(
        name="John Doe",
        phone_number="+1234567890",
        email="john@example.com"
    )
    db.add(contact)
    db.commit()

    retrieved_contact = db.query(Contact).filter_by(name="John Doe").first()
    assert retrieved_contact is not None
    assert retrieved_contact.phone_number == "+1234567890"
    assert retrieved_contact.email == "john@example.com"
    assert retrieved_contact.created_at is not None
    assert retrieved_contact.updated_at is not None


def test_interaction_model(db: Session):
    contact = Contact(name="Jane Doe", phone_number="+9876543210")
    db.add(contact)
    db.commit()

    interaction = Interaction(
        contact_id=contact.contact_id,
        message="Test interaction",
        direction="INBOUND",
        status=Status.DELIVERED
    )
    db.add(interaction)
    db.commit()

    retrieved_interaction = db.query(
        Interaction
    ).filter_by(
        message="Test interaction"
    ).first()
    assert retrieved_interaction is not None
    assert retrieved_interaction.contact_id == contact.contact_id
    assert retrieved_interaction.direction == "INBOUND"
    assert retrieved_interaction.status == Status.DELIVERED
    assert retrieved_interaction.timestamp is not None


def test_message_model(db: Session):
    contact = Contact(name="Alice", email="alice@example.com")
    db.add(contact)
    db.commit()

    message = Message(
        contact_id=contact.contact_id,
        type=MessageType.EMAIL,
        direction=MessageDirection.OUTBOUND,
        content="Test email content",
        html_content="<p>Test email content</p>",
        subject="Test Subject"
    )
    db.add(message)
    db.commit()

    retrieved_message = db.query(
        Message
    ).filter_by(
        subject="Test Subject").first()
    assert retrieved_message is not None
    assert retrieved_message.contact_id == contact.contact_id
    assert retrieved_message.type == MessageType.EMAIL
    assert retrieved_message.direction == MessageDirection.OUTBOUND
    assert retrieved_message.content == "Test email content"
    assert retrieved_message.html_content == "<p>Test email content</p>"
    assert retrieved_message.status == Status.PENDING
    assert retrieved_message.timestamp is not None


def test_blast_model(db: Session):
    blast = Blast(
        name="Test Blast",
        type=MessageType.SMS,
        content="Test blast content",
        scheduled_time=datetime.now(ZoneInfo("UTC")) + timedelta(hours=1)
    )
    db.add(blast)
    db.commit()

    retrieved_blast = db.query(Blast).filter_by(name="Test Blast").first()
    assert retrieved_blast is not None
    assert retrieved_blast.type == MessageType.SMS
    assert retrieved_blast.content == "Test blast content"
    assert retrieved_blast.status == Status.PENDING
    assert retrieved_blast.created_at is not None
    assert retrieved_blast.scheduled_time is not None


def test_blast_recipient_model(db: Session):
    contact = Contact(name="Bob", phone_number="+1122334455")
    blast = Blast(
        name="Test Blast",
        type=MessageType.SMS,
        content="Test content"
    )
    db.add_all([contact, blast])
    db.commit()

    blast_recipient = BlastRecipient(
        blast_id=blast.blast_id,
        contact_id=contact.contact_id
    )
    db.add(blast_recipient)
    db.commit()

    retrieved_blast = db.query(Blast).filter_by(name="Test Blast").first()
    assert retrieved_blast is not None
    assert len(retrieved_blast.recipients) == 1
    assert retrieved_blast.recipients[0].name == "Bob"

    retrieved_contact = db.query(Contact).filter_by(name="Bob").first()
    assert retrieved_contact is not None
    assert len(retrieved_contact.blast_recipients) == 1
    assert retrieved_contact.blast_recipients[0].blast.name == "Test Blast"

# Add more model tests as needed
