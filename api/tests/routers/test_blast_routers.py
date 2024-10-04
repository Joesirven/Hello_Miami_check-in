import pytest
from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


def test_create_blast():
    response = client.post("/blasts/", json={
        "name": "Test Blast",
        "type": "SMS",
        "content": "Test content",
        "recipient_ids": [1, 2, 3],
        "scheduled_time": "2024-09-30T12:00:00Z",

    })
    assert response.status_code == 200
    assert response.json()["name"] == "Test Blast"
    assert response.json()["type"] == "SMS"
    assert response.json()["content"] == "Test content"


def test_read_blast():
    # First, create a blast
    create_response = client.post("/blasts/", json={
        "name": "Test Blast",
        "type": "SMS",
        "content": "Test content",
        "recipient_ids": [1, 2, 3]
    })
    blast_id = create_response.json()["blast_id"]

    # Then, read the blast
    response = client.get(f"/blasts/{blast_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Blast"
    assert response.json()["blast_id"] == blast_id


def test_read_non_existent_blast():
    response = client.get("/blasts/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Blast not found"


def test_read_blasts():
    # Create multiple blasts
    for i in range(3):
        client.post("/blasts/", json={
            "name": f"Test Blast {i}",
            "type": "SMS",
            "content": f"Test content {i}",
            "recipient_ids": [1, 2, 3]
        })

    response = client.get("/blasts/")
    assert response.status_code == 200
    assert len(response.json()) >= 3
    assert response.json()[0]["name"] == "Test Blast 0"


def test_update_blast():
    # First, create a blast
    create_response = client.post("/blasts/", json={
        "name": "Test Blast",
        "type": "SMS",
        "content": "Test content",
        "recipient_ids": [1, 2, 3]
    })
    blast_id = create_response.json()["blast_id"]

    # Then, update the blast
    update_response = client.put(f"/blasts/{blast_id}", json={
        "name": "Updated Blast",
        "type": "EMAIL",
        "content": "Updated content",
        "recipient_ids": [1, 2, 3, 4]
    })
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Blast"
    assert update_response.json()["type"] == "EMAIL"
    assert update_response.json()["content"] == "Updated content"


def test_update_non_existent_blast():
    response = client.put("/blasts/9999", json={
        "name": "Updated Blast",
        "type": "SMS",
        "content": "Updated content",
        "recipient_ids": [1, 2, 3]
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Blast not found"


def test_send_blast():
    # First, create a blast
    create_response = client.post("/blasts/", json={
        "name": "Test Blast",
        "type": "SMS",
        "content": "Test content",
        "recipient_ids": [1, 2, 3]
    })
    blast_id = create_response.json()["blast_id"]

    # Then, send the blast
    send_response = client.post(f"/blasts/{blast_id}/send")
    assert send_response.status_code == 200
    assert send_response.json()["status"] == "SENT"


def test_send_non_existent_blast():
    response = client.post("/blasts/9999/send")
    assert response.status_code == 404
    assert response.json()["detail"] == "Blast not found"

# Add more tests for other router endpoints
