import pytest
from sqlalchemy.orm import Session
from api.queries import messages
from api.schemas import MessageCreate
from api.models import MessageType, MessageDirection
from datetime import datetime, timezone


def test_create_message(db: Session, mocker):
    # Mock send_sms and HTMLEmail.send functions
    mock_send_sms = mocker.patch('api.queries.messages.send_sms')
    mock_html_email_send = mocker.patch('api.queries.messages.HTMLEmail.send')

    message_data = MessageCreate(
        contact_id=1,
        type=MessageType.SMS,
        content="Test message",
        direction=MessageDirection.OUTBOUND
    )
    created_message = messages.create_message(
        db, message_data, "Test Sender", datetime.utcnow())
    assert created_message.content == "Test message"
    assert created_message.type == MessageType.SMS
    assert mock_send_sms.called

    # Test email message
    email_message_data = MessageCreate(
        contact_id=1,
        type=MessageType.EMAIL,
        content="Test email",
        html_content="<p>Test email</p>",
        subject="Test Subject",
        direction=MessageDirection.OUTBOUND
    )
    created_email_message = messages.create_message(
        db,
        email_message_data,
        "Test Sender",
        datetime.now(timezone.utc)
    )
    assert created_email_message.content == "Test email"
    assert created_email_message.type == MessageType.EMAIL
    assert mock_html_email_send.called


def test_get_messages(db: Session):
    # Create test messages
    message_data = [
        MessageCreate(
            contact_id=1,
            type=MessageType.SMS,
            content=f"Test message {i}",
            direction=MessageDirection.OUTBOUND
        )
        for i in range(5)
    ]
    for message in message_data:
        messages.create_message(
            db,
            message,
            "Test Sender",
            datetime.now(timezone.utc)
        )

    retrieved_messages = messages.get_messages(db, skip=1, limit=3)
    assert len(retrieved_messages) == 3
    assert retrieved_messages[0].content == "Test message 1"
    assert retrieved_messages[-1].content == "Test message 3"


def test_get_message(db: Session):
    message_data = MessageCreate(
        contact_id=1,
        type=MessageType.SMS,
        content="Test message",
        direction=MessageDirection.OUTBOUND
    )
    created_message = messages.create_message(
        db,
        message_data,
        "Test Sender",
        datetime.now(timezone.utc)
    )

    retrieved_message = messages.get_message(db, created_message.message_id)
    assert retrieved_message is not None
    assert retrieved_message.content == "Test message"
    assert retrieved_message.type == MessageType.SMS


def test_update_message(db: Session):
    message_data = MessageCreate(
        contact_id=1,
        type=MessageType.SMS,
        content="Original message",
        direction=MessageDirection.OUTBOUND
    )
    created_message = messages.create_message(
        db,
        message_data,
        "Test Sender",
        datetime.now(timezone.utc)
    )

    update_data = MessageCreate(
        contact_id=1,
        type=MessageType.EMAIL,
        content="Updated message",
        direction=MessageDirection.OUTBOUND
    )
    updated_message = messages.update_message(
        db,
        created_message.message_id,
        update_data
    )
    assert updated_message.content == "Updated message"
    assert updated_message.type == MessageType.EMAIL


def test_delete_message(db: Session):
    message_data = MessageCreate(
        contact_id=1,
        type=MessageType.SMS,
        content="Message to delete",
        direction=MessageDirection.OUTBOUND
    )
    created_message = messages.create_message(
        db,
        message_data,
        "Test Sender",
        datetime.now(timezone.utc)
    )

    deleted_message = messages.delete_message(db, created_message.message_id)
    assert deleted_message.content == "Message to delete"

    # Verify the message is deleted
    assert messages.get_message(db, created_message.message_id) is None
