import pytest
from sqlalchemy.orm import Session
from api.queries import interactions
from api.schemas import InteractionCreate
from api.models import Contact


def test_create_interaction(db: Session):
    # Create a test contact first
    contact = Contact(name="Test Contact", phone_number="+1234567890")
    db.add(contact)
    db.commit()

    interaction_data = InteractionCreate(
        contact_id=contact.contact_id,
        message="Test interaction",
        direction="OUTBOUND",
        status="PENDING"
    )
    created_interaction = interactions.create_interaction(db, interaction_data)
    assert created_interaction.message == "Test interaction"
    assert created_interaction.direction == "OUTBOUND"
    assert created_interaction.status == "PENDING"
    assert created_interaction.contact_id == contact.contact_id


def test_get_interactions_by_contact(db: Session):
    # Create a test contact
    contact = Contact(name="Test Contact", phone_number="+1234567890")
    db.add(contact)
    db.commit()

    # Create test interactions
    interaction_data = [
        InteractionCreate(
            contact_id=contact.contact_id,
            message=f"Test interaction {i}",
            direction="OUTBOUND",
            status="PENDING"
        ) for i in range(5)
    ]
    for interaction in interaction_data:
        interactions.create_interaction(db, interaction)

    retrieved_interactions = interactions.get_interactions_by_contact(
        db,
        contact.contact_id,
        skip=1,
        limit=3
    )
    assert len(retrieved_interactions) == 3
    assert retrieved_interactions[0].message == "Test interaction 1"
    assert retrieved_interactions[-1].message == "Test interaction 3"
