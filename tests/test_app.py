import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_200():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_succeeds():
    email = "test_student@example.com"
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    activities_response = client.get("/activities").json()
    assert email in activities_response["Chess Club"]["participants"]


def test_duplicate_signup_returns_400():
    email = "duplicate_student@example.com"
    first_response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )
    assert first_response.status_code == 200

    second_response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_succeeds():
    email = "remove_student@example.com"
    signup_response = client.post(
        "/activities/Programming%20Class/signup",
        params={"email": email},
    )
    assert signup_response.status_code == 200

    delete_response = client.delete(
        "/activities/Programming%20Class/signup",
        params={"email": email},
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Unregistered {email} from Programming Class"

    activities_response = client.get("/activities").json()
    assert email not in activities_response["Programming Class"]["participants"]


def test_unregister_missing_participant_returns_404():
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "missing_student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
