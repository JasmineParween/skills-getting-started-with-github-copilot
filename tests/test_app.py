def test_root_redirects_to_static():
    from fastapi.testclient import TestClient
    from src.app import app

    client = TestClient(app)
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "Programming Class" in response.json()


def test_signup_for_activity_adds_participant(client):
    email = "newstudent@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}

    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_bad_request(client):
    email = "emma@mergington.edu"
    response = client.post(
        "/activities/Programming%20Class/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_from_activity_removes_participant(client):
    email = "michael@mergington.edu"
    response = client.delete(
        "/activities/Chess%20Club/unregister",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}

    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_missing_registration_returns_not_found(client):
    response = client.delete(
        "/activities/Chess%20Club/unregister",
        params={"email": "not_registered@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"


def test_activity_not_found_returns_not_found_on_signup(client):
    response = client.post(
        "/activities/Nonexistent%20Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_activity_not_found_returns_not_found_on_unregister(client):
    response = client.delete(
        "/activities/Nonexistent%20Activity/unregister",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
