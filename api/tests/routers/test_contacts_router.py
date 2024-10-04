import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_create_contact():
    response = client.post("/contacts/", json={
        "name": "John Doe",
        "phone_number": "+1234567890",
        "email": "john@example.com"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "John Doe"
    assert response.json()["phone_number"] == "+1234567890"
    assert response.json()["email"] == "john@example.com"


def test_read_contacts():
    response = client.get("/contacts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_read_contact():
    # First, create a contact
    create_response = client.post("/contacts/", json={
        "name": "Jane Doe",
        "phone_number": "+0987654321",
        "email": "jane@example.com"
    })
    contact_id = create_response.json()["contact_id"]

    # Then, read the contact
    response = client.get(f"/contacts/{contact_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Jane Doe"
    assert response.json()["contact_id"] == contact_id


def test_update_contact():
    # First, create a contact
    create_response = client.post("/contacts/", json={
        "name": "Bob Smith",
        "phone_number": "+1122334455",
        "email": "bob@example.com"
    })
    contact_id = create_response.json()["contact_id"]

    # Then, update the contact
    update_response = client.put(f"/contacts/{contact_id}", json={
        "name": "Robert Smith",
        "email": "robert@example.com"
    })
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Robert Smith"
    assert update_response.json()["email"] == "robert@example.com"
    assert update_response.json()["phone_number"] == "+1122334455"


def test_delete_contact():
    # First, create a contact
    create_response = client.post("/contacts/", json={
        "name": "Alice Johnson",
        "phone_number": "+9988776655",
        "email": "alice@example.com"
    })
    contact_id = create_response.json()["contact_id"]

    # Then, delete the contact
    delete_response = client.delete(f"/contacts/{contact_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["name"] == "Alice Johnson"

    # Verify the contact is deleted
    get_response = client.get(f"/contacts/{contact_id}")
    assert get_response.status_code == 404
