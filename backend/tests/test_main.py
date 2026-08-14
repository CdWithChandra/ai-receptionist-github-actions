from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert "message" in data


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert "version" in data


def test_get_appointments():
    response = client.get("/appointments")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_update_delete_booking():
    """
    Test the complete appointment lifecycle:
    Create -> Retrieve -> Update -> Delete
    """

    unique_name = f"Test Customer {uuid4().hex[:8]}"

    create_payload = {
        "customer_name": unique_name,
        "appointment_date": "2099-12-31",
        "appointment_time": "11:59 PM",
    }

    # -------------------------
    # CREATE
    # -------------------------

    create_response = client.post(
        "/booking",
        json=create_payload,
    )

    assert create_response.status_code == 200

    create_data = create_response.json()

    assert create_data["status"] == "success"
    assert "message" in create_data

    # -------------------------
    # RETRIEVE
    # -------------------------

    get_response = client.get("/appointments")

    assert get_response.status_code == 200

    appointments = get_response.json()

    created_appointment = next(
        (
            appointment
            for appointment in appointments
            if appointment["customer_name"] == unique_name
        ),
        None,
    )

    assert created_appointment is not None

    appointment_id = created_appointment["id"]

    # -------------------------
    # UPDATE
    # -------------------------

    update_payload = {
        "customer_name": unique_name,
        "appointment_date": "2099-01-02",
        "appointment_time": "11:00 AM",
    }

    update_response = client.put(
        f"/booking/{appointment_id}",
        json=update_payload,
    )

    assert update_response.status_code == 200

    update_data = update_response.json()

    assert update_data["status"] == "success"
    assert "message" in update_data

    # -------------------------
    # DELETE
    # -------------------------

    delete_response = client.delete(
        f"/booking/{appointment_id}"
    )

    assert delete_response.status_code == 200

    delete_data = delete_response.json()

    assert delete_data["status"] == "success"
    assert "message" in delete_data


def test_chat_validation_error():
    """
    Verify that /chat rejects an invalid request body.
    This does not call OpenAI.
    """

    response = client.post(
        "/chat",
        json={},
    )

    assert response.status_code == 422


def test_booking_validation_error():
    """
    Verify that /booking rejects an invalid request body.
    """

    response = client.post(
        "/booking",
        json={},
    )

    assert response.status_code == 422


def test_update_nonexistent_appointment():
    """
    Verify behavior when attempting to update
    an appointment that does not exist.
    """

    payload = {
        "customer_name": "Nonexistent Customer",
        "appointment_date": "2099-01-10",
        "appointment_time": "10:00 AM",
    }

    response = client.put(
        "/booking/999999999",
        json=payload,
    )

    assert response.status_code in [404, 400]


def test_delete_nonexistent_appointment():
    """
    Verify behavior when attempting to delete
    an appointment that does not exist.
    """

    response = client.delete(
        "/booking/999999999"
    )

    assert response.status_code in [404, 400]