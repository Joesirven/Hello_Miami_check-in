import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.models import Contact
from sqlalchemy.orm import Session


client = TestClient(app)


def test_send_message(db: Session):
    # Create a test contact
    contact = Contact(
        name="Test Contact",
        phone_number="+1234567890"
    )
    db.add(contact)
    db.commit()

    response = client.post("/interactions/send", json={
        "contact_id": contact.contact_id,
        "message": "Test message",
        "direction": "OUTBOUND",
        "status": "PENDING"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Test message"
    assert response.json()["direction"] == "OUTBOUND"
    assert response.json()["status"] == "PENDING"
    assert response.json()["contact_id"] == contact.contact_id


def test_send_message_non_existent_contact(db: Session):
    response = client.post("/interactions/send", json={
        "contact_id": 9999,  # Non-existent contact ID
        "message": "Test message",
        "direction": "OUTBOUND",
        "status": "PENDING"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found"
