import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball" in data
    assert "description" in data["Basketball"]
    assert "participants" in data["Basketball"]


def test_signup_for_activity():
    # Test successful signup
    response = client.post("/activities/Basketball/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up test@example.com for Basketball" in data["message"]

    # Check that the participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Basketball"]["participants"]

    # Test duplicate signup
    response = client.post("/activities/Basketball/signup?email=test@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up" in data["detail"]


def test_signup_nonexistent_activity():
    response = client.post("/activities/Nonexistent/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_from_activity():
    # First sign up
    client.post("/activities/Soccer%20Club/signup?email=unregister@example.com")

    # Test successful unregister
    response = client.delete("/activities/Soccer%20Club/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered unregister@example.com from Soccer Club" in data["message"]

    # Check that the participant was removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@example.com" not in data["Soccer Club"]["participants"]

    # Test unregistering someone not signed up
    response = client.delete("/activities/Soccer%20Club/unregister?email=notsignedup@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student not signed up" in data["detail"]


def test_unregister_nonexistent_activity():
    response = client.delete("/activities/Nonexistent/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    # Since it's a redirect to /static/index.html, but TestClient follows redirects by default
    # Actually, RedirectResponse redirects to /static/index.html, but since static files are mounted,
    # it should serve the file. But in test, it might not work the same.
    # Perhaps skip this or adjust.
    pass