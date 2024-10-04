import pytest
from sqlalchemy.orm import Session
from api.queries import contacts
from api.schemas import ContactCreate, ContactUpdate


def test_create_contact(db: Session):
    contact_data = ContactCreate(
        name="John Doe",
        phone_number="+1234567890",
        email="john@example.com"
    )
    created_contact = contacts.create_contact(db, contact_data)
    assert created_contact.name == "John Doe"
    assert created_contact.phone_number == "+1234567890"
    assert created_contact.email == "john@example.com"


def test_get_contacts(db: Session):
    # Create test contacts
    contact_data = [
        ContactCreate(
            name=f"Contact {i}",
            phone_number=f"+123456789{i}",
            email=f"contact{i}@example.com"
        ) for i in range(5)
    ]
    for contact in contact_data:
        contacts.create_contact(db, contact)

    retrieved_contacts = contacts.get_contacts(db, skip=1, limit=3)
    assert len(retrieved_contacts) == 3
    assert retrieved_contacts[0].name == "Contact 1"
    assert retrieved_contacts[-1].name == "Contact 3"


def test_get_contact(db: Session):
    contact_data = ContactCreate(
        name="Jane Doe",
        phone_number="+0987654321",
        email="jane@example.com"
    )
    created_contact = contacts.create_contact(db, contact_data)

    retrieved_contact = contacts.get_contact(db, created_contact.contact_id)
    assert retrieved_contact is not None
    assert retrieved_contact.name == "Jane Doe"
    assert retrieved_contact.phone_number == "+0987654321"


def test_update_contact(db: Session):
    contact_data = ContactCreate(
        name="Bob Smith",
        phone_number="+1122334455",
        email="bob@example.com"
    )
    created_contact = contacts.create_contact(db, contact_data)

    update_data = ContactUpdate(
        name="Robert Smith",
        email="robert@example.com"
    )
    updated_contact = contacts.update_contact(
        db,
        created_contact.contact_id,
        update_data
    )
    assert updated_contact.name == "Robert Smith"
    assert updated_contact.email == "robert@example.com"
    assert updated_contact.phone_number == "+1122334455"


def test_delete_contact(db: Session):
    contact_data = ContactCreate(
        name="Alice Johnson",
        phone_number="+9988776655",
        email="alice@example.com"
    )
    created_contact = contacts.create_contact(db, contact_data)

    deleted_contact = contacts.delete_contact(db, created_contact.contact_id)
    assert deleted_contact.name == "Alice Johnson"

    # Verify the contact is deleted
    assert contacts.get_contact(db, created_contact.contact_id) is None
