import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_create_message():
    response = client.post("/messages/", json={
        "contact_id": 1,
        "type": "SMS",
        "content": "Test message",
        "direction": "OUTBOUND"
    })
    assert response.status_code == 200
    assert response.json()["content"] == "Test message"
    assert response.json()["type"] == "SMS"


def test_read_messages():
    response = client.get("/messages/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_read_message():
    # First, create a message
    create_response = client.post("/messages/", json={
        "contact_id": 1,
        "type": "SMS",
        "content": "Test message",
        "direction": "OUTBOUND"
    })
    message_id = create_response.json()["message_id"]

    # Then, read the message
    response = client.get(f"/messages/{message_id}")
    assert response.status_code == 200
    assert response.json()["content"] == "Test message"
    assert response.json()["message_id"] == message_id


def test_update_message():
    # First, create a message
    create_response = client.post("/messages/", json={
        "contact_id": 1,
        "type": "SMS",
        "content": "Original message",
        "direction": "OUTBOUND"
    })
    message_id = create_response.json()["message_id"]

    # Then, update the message
    update_response = client.put(f"/messages/{message_id}", json={
        "content": "Updated message",
        "type": "EMAIL"
    })
    assert update_response.status_code == 200
    assert update_response.json()["content"] == "Updated message"
    assert update_response.json()["type"] == "EMAIL"


def test_delete_message():
    # First, create a message
    create_response = client.post("/messages/", json={
        "contact_id": 1,
        "type": "SMS",
        "content": "Message to delete",
        "direction": "OUTBOUND"
    })
    message_id = create_response.json()["message_id"]

    # Then, delete the message
    delete_response = client.delete(f"/messages/{message_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["content"] == "Message to delete"

    # Verify the message is deleted
    get_response = client.get(f"/messages/{message_id}")
    assert get_response.status_code == 404


def test_send_message():
    response = client.post("/messages/send", json={
        "contact_id": 1,
        "type": "SMS",
        "content": "Test message to send",
        "direction": "OUTBOUND"
    })
    assert response.status_code == 200
    assert response.json()["content"] == "Test message to send"
    assert response.json()["status"] == "PENDING"


def test_get_scheduled_messages():
    response = client.get("/messages/schedule")
    assert response.status_code == 501
    assert response.json()["detail"] == "Not implemented"
