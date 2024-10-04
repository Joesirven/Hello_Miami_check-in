import pytest
from pydantic import ValidationError
from datetime import datetime
from api.schemas import (
    MessageType, MessageDirection, InteractionStatus,
    ContactCreate, ContactUpdate, InteractionCreate, MessageCreate,
    BlastCreate, BlastUpdate, BlastDelete, BlastSchedule, BlastCancel
)


def test_contact_create_schema():
    valid_data = {
        "name": "John Doe",
        "phone_number": "+1234567890"
    }
    contact = ContactCreate(**valid_data)
    assert contact.name == "John Doe"
    assert contact.phone_number == "+1234567890"

    with pytest.raises(ValidationError):
        ContactCreate(name="Invalid")


def test_contact_update_schema():
    valid_data = {
        "name": "Jane Doe"
    }
    contact = ContactUpdate(**valid_data)
    assert contact.name == "Jane Doe"
    assert contact.phone_number is None


def test_interaction_create_schema():
    valid_data = {
        "contact_id": 1,
        "message": "Test message",
        "direction": MessageDirection.INBOUND
    }
    interaction = InteractionCreate(**valid_data)
    assert interaction.contact_id == 1
    assert interaction.message == "Test message"
    assert interaction.direction == MessageDirection.INBOUND

    with pytest.raises(ValidationError):
        InteractionCreate(
            contact_id="invalid",
            message="Test",
            direction="INVALID"
        )


def test_message_create_schema():
    valid_data = {
        "contact_id": 1,
        "type": MessageType.SMS,
        "direction": MessageDirection.OUTBOUND,
        "content": "Test content"
    }
    message = MessageCreate(**valid_data)
    assert message.contact_id == 1
    assert message.type == MessageType.SMS
    assert message.direction == MessageDirection.OUTBOUND
    assert message.content == "Test content"

    with pytest.raises(ValidationError):
        MessageCreate(
            contact_id="invalid",
            type="INVALID",
            direction="INVALID",
            content=""
        )


def test_blast_create_schema():
    valid_data = {
        "name": "Test Blast",
        "type": MessageType.SMS,
        "content": "Test content",
        "recipient_ids": [1, 2, 3]
    }
    blast = BlastCreate(**valid_data)
    assert blast.name == "Test Blast"
    assert blast.type == MessageType.SMS
    assert blast.content == "Test content"
    assert blast.recipient_ids == [1, 2, 3]

    with pytest.raises(ValidationError):
        BlastCreate(
            name="Invalid",
            type="INVALID",
            content="",
            recipient_ids="invalid"
        )


def test_blast_update_schema():
    valid_data = {
        "name": "Updated Blast",
        "content": "Updated content",
        "status": InteractionStatus.SENT
    }
    blast = BlastUpdate(**valid_data)
    assert blast.name == "Updated Blast"
    assert blast.content == "Updated content"
    assert blast.status == InteractionStatus.SENT


def test_blast_delete_schema():
    valid_data = {
        "id": 1
    }
    blast_delete = BlastDelete(**valid_data)
    assert blast_delete.id == 1

    with pytest.raises(ValidationError):
        BlastDelete(id="invalid")


def test_blast_schedule_schema():
    valid_data = {
        "id": 1,
        "scheduled_time": datetime.now()
    }
    blast_schedule = BlastSchedule(**valid_data)
    assert blast_schedule.id == 1
    assert isinstance(blast_schedule.scheduled_time, datetime)

    with pytest.raises(ValidationError):
        BlastSchedule(id="invalid", scheduled_time="not a datetime")


def test_blast_cancel_schema():
    valid_data = {
        "id": 1
    }
    blast_cancel = BlastCancel(**valid_data)
    assert blast_cancel.id == 1

    with pytest.raises(ValidationError):
        BlastCancel(id="invalid")

# Add more schema tests
