import pytest
from fastapi.testclient import TestClient


def test_root_redirect(client: TestClient):
    """Test root endpoint redirects to static index.html"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/static/index.html"


def test_get_activities(client: TestClient):
    """Test getting all activities returns correct data"""
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # All 9 activities

    # Check that all expected activities are present
    expected_activities = [
        "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
        "Swimming Club", "Art Studio", "Drama Club", "Debate Team", "Science Club"
    ]
    assert set(data.keys()) == set(expected_activities)

    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success(client: TestClient):
    """Test successful signup for an activity"""
    # Arrange
    email = "test@example.com"
    activity = "Basketball Team"
    
    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity}" in data["message"]
    
    # Verify the signup was recorded
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity]["participants"]


def test_signup_activity_not_found(client: TestClient):
    """Test signup for non-existent activity"""
    # Arrange
    email = "test@example.com"
    activity = "NonExistent Activity"
    
    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_signup_duplicate_email(client: TestClient):
    """Test signup with email already registered"""
    # Arrange
    email = "duplicate@example.com"
    activity = "Art Studio"
    
    # Act - First signup
    client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Act - Second signup with same email
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Email already signed up for this activity"


def test_signup_different_activity_same_email(client: TestClient):
    """Test that same email can signup for different activities"""
    # Arrange
    email = "multi@example.com"
    activity1 = "Drama Club"
    activity2 = "Debate Team"
    
    # Act - Signup for first activity
    client.post(
        f"/activities/{activity1}/signup",
        params={"email": email}
    )
    
    # Act - Signup for second activity with same email
    response = client.post(
        f"/activities/{activity2}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    
    # Verify both signups
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity1]["participants"]
    assert email in activities[activity2]["participants"]


def test_unregister_success(client: TestClient):
    """Test successful unregistration from an activity"""
    # Arrange
    email = "unregister@example.com"
    activity = "Swimming Club"
    
    # Act - First signup
    client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Act - Then unregister
    response = client.delete(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Unregistered {email} from {activity}" in data["message"]
    
    # Verify the unregistration
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity]["participants"]


def test_unregister_activity_not_found(client: TestClient):
    """Test unregister from non-existent activity"""
    # Arrange
    email = "test@example.com"
    activity = "NonExistent Activity"
    
    # Act
    response = client.delete(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_unregister_email_not_signed_up(client: TestClient):
    """Test unregister email that is not signed up"""
    # Arrange
    email = "notsignedup@example.com"
    activity = "Science Club"
    
    # Act
    response = client.delete(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Email not signed up for this activity"


def test_unregister_from_different_activity(client: TestClient):
    """Test unregister from activity where email is signed up for different activity"""
    # Arrange
    email = "different@example.com"
    activity1 = "Programming Class"
    activity2 = "Gym Class"
    
    # Act - Signup for one activity
    client.post(
        f"/activities/{activity1}/signup",
        params={"email": email}
    )
    
    # Act - Try to unregister from different activity
    response = client.delete(
        f"/activities/{activity2}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Email not signed up for this activity"