import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0

    # Check that each activity has required fields
    for name, details in activities.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)


def test_signup_for_activity():
    """Test signing up for an activity"""
    # First, get activities to find a valid activity name
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    # Sign up a new student
    email = "test@student.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]

    # Verify the student was added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate():
    """Test signing up for the same activity twice"""
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    email = "duplicate@student.edu"
    # First signup
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Second signup should fail
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]


def test_signup_invalid_activity():
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/NonExistentActivity/signup?email=test@student.edu")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # First, get activities and sign up
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    email = "unregister@student.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Now unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]

    # Verify the student was removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_not_signed_up():
    """Test unregistering a student who is not signed up"""
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    email = "notsignedup@student.edu"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    result = response.json()
    assert "not signed up" in result["detail"]


def test_unregister_invalid_activity():
    """Test unregistering from a non-existent activity"""
    response = client.delete("/activities/NonExistentActivity/unregister?email=test@student.edu")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_root_redirect():
    """Test that root redirects to static index"""
    response = client.get("/")
    assert response.status_code == 200
    # The redirect response should contain the static file content
    assert "Mergington High School" in response.text


def test_static_files():
    """Test that static files are served"""
    response = client.get("/static/styles.css")
    assert response.status_code == 200
    assert "box-sizing" in response.text

    response = client.get("/static/app.js")
    assert response.status_code == 200
    assert "DOMContentLoaded" in response.text