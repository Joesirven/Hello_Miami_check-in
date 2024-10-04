import pytest
from sqlalchemy.orm import Session
from api.queries import blasts
from api.schemas import BlastCreate, BlastUpdate
from api.models import Blast, Contact, MessageType, Status


@pytest.fixture
def test_create_blast(db: Session):
    # Create test contacts
    contacts = [
        Contact(
            name=f"Contact {i}",
            phone_number=f"+123456789{i}"
        ) for i in range(3)
    ]
    db.add_all(contacts)
    db.commit()

    blast_data = BlastCreate(
        name="Test Blast",
        type=MessageType.SMS,
        content="Test content",
        recipient_ids=[contact.contact_id for contact in contacts]
    )
    created_blast = blasts.create_blast(db, blast_data)
    assert created_blast.name == "Test Blast"
    assert created_blast.type == MessageType.SMS
    assert created_blast.content == "Test content"
    assert len(created_blast.recipients) == 3


def test_send_blast(db: Session, mocker):
    # Mock send_sms and send_email functions
    mock_send_sms = mocker.patch('api.queries.blasts.send_sms')
    mock_send_email = mocker.patch('api.queries.blasts.send_email')

    # Create a test blast with recipients
    contacts = [
        Contact(
            name=f"Contact {i}",
            phone_number=f"+123456789{i}",
            email=f"contact{i}@example.com"
        ) for i in range(2)
    ]
    blast = Blast(
        name="Test Blast",
        type=MessageType.SMS,
        content="Test content"
    )
    blast.recipients.extend(contacts)
    db.add(blast)
    db.add_all(contacts)
    db.commit()

    sent_blast = blasts.send_blast(db, blast.blast_id)
    assert sent_blast is not None
    assert sent_blast.status == Status.SENT
    assert mock_send_sms.call_count == 2
    assert mock_send_email.call_count == 0

    # Test email blast
    blast.type = MessageType.EMAIL
    db.commit()
    blasts.send_blast(db, blast.blast_id)
    assert mock_send_sms.call_count == 2
    assert mock_send_email.call_count == 2


def test_get_blasts(db: Session):
    # Create test blasts
    test_blasts = [
        Blast(
            name=f"Test Blast {i}",
            type=MessageType.SMS,
            content=f"Content {i}"
        ) for i in range(5)
    ]
    db.add_all(test_blasts)
    db.commit()

    retrieved_blasts = blasts.get_blasts(db, skip=1, limit=3)
    assert len(retrieved_blasts) == 3
    assert retrieved_blasts[0].name == "Test Blast 1"
    assert retrieved_blasts[-1].name == "Test Blast 3"


def test_get_blast(db: Session):
    blast = Blast(
        name="Test Blast",
        type=MessageType.SMS,
        content="Test content"
    )
    db.add(blast)
    db.commit()

    retrieved_blast = blasts.get_blast(db, blast.blast_id)
    assert retrieved_blast is not None
    assert retrieved_blast.name == "Test Blast"
    assert retrieved_blast.content == "Test content"

    non_existent_blast = blasts.get_blast(db, 9999)
    assert non_existent_blast is None


def test_update_blast(db: Session):
    blast = Blast(
        name="Test Blast",
        type=MessageType.SMS,
        content="Test content"
    )
    db.add(blast)
    db.commit()

    update_data = BlastUpdate(
        name="Updated Blast",
        content="Updated content",
        status=Status.SENT
    )
    updated_blast = blasts.update_blast(db, blast.blast_id, update_data)
    assert updated_blast is not None
    assert updated_blast.name == "Updated Blast"
    assert updated_blast.content == "Updated content"
    assert updated_blast.status == Status.SENT


def test_delete_blast(db: Session):
    blast = Blast(
        name="Test Blast",
        type=MessageType.SMS,
        content="Test content"
    )
    db.add(blast)
    db.commit()

    deleted_blast = blasts.delete_blast(db, blast.blast_id)
    assert deleted_blast is not None
    assert deleted_blast.name == "Test Blast"

    # Verify the blast is deleted
    assert blasts.get_blast(db, blast.blast_id) is None

    # Try to delete a non-existent blast
    non_existent_delete = blasts.delete_blast(db, 9999)
    assert non_existent_delete is None

# Add more tests for other query functions
