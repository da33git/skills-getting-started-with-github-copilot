from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_get_activities_returns_data():
    # Arrange: No special setup needed as activities are predefined

    # Act: Make GET request to /activities
    response = client.get("/activities")

    # Assert: Check response status and data structure
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    # Arrange: Select an activity and email for signup
    activity = "Soccer Club"
    email = "teststudent@mergington.edu"

    # Act: Make POST request to signup endpoint
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )

    # Assert: Check response and that participant was added
    assert response.status_code == 200
    assert email in activities[activity]["participants"]

    # Cleanup: Remove the test participant
    activities[activity]["participants"].remove(email)


def test_signup_duplicate_returns_400():
    # Arrange: Select an activity and email, first signup
    activity = "Basketball Team"
    email = "duplicate@mergington.edu"

    # Act: First signup (should succeed)
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )
    assert response.status_code == 200

    # Act: Attempt duplicate signup
    duplicate_response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )

    # Assert: Check that duplicate returns 400 error
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"

    # Cleanup: Remove the test participant
    activities[activity]["participants"].remove(email)


def test_remove_participant():
    # Arrange: Select an activity and email, first signup
    activity = "Art Club"
    email = "removeme@mergington.edu"

    # Act: Signup first
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )
    assert response.status_code == 200

    # Act: Remove the participant
    delete_response = client.delete(
        f"/activities/{activity}/participants/{email}"
    )

    # Assert: Check response and that participant was removed
    assert delete_response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange: Select an activity and a non-existent email

    # Act: Attempt to remove non-existent participant
    response = client.delete(
        "/activities/Art Club/participants/noone@mergington.edu"
    )

    # Assert: Check that it returns 404
    assert response.status_code == 404