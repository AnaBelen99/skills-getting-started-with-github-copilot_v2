import urllib.parse
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_delete_participant():
    activity = "Chess Club"
    email = "test_user@example.com"
    act_quoted = urllib.parse.quote(activity, safe="")

    # Ensure participant not present
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    if email in participants:
        client.delete(f"/activities/{act_quoted}/participants?email={urllib.parse.quote(email, safe='')}" )

    # Sign up
    r = client.post(f"/activities/{act_quoted}/signup?email={urllib.parse.quote(email, safe='')}")
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # Verify present
    r2 = client.get("/activities")
    assert email in r2.json()[activity]["participants"]

    # Duplicate signup should fail
    r3 = client.post(f"/activities/{act_quoted}/signup?email={urllib.parse.quote(email, safe='')}")
    assert r3.status_code == 400

    # Remove participant
    r4 = client.delete(f"/activities/{act_quoted}/participants?email={urllib.parse.quote(email, safe='')}")
    assert r4.status_code == 200
    assert "Unregistered" in r4.json().get("message", "")

    # Ensure removed
    r5 = client.get("/activities")
    assert email not in r5.json()[activity]["participants"]


def test_delete_nonexistent_participant():
    activity = "Chess Club"
    email = "nonexistent_user@example.com"
    act_quoted = urllib.parse.quote(activity, safe="")

    # Ensure not present
    r = client.get("/activities")
    if email in r.json()[activity]["participants"]:
        client.delete(f"/activities/{act_quoted}/participants?email={urllib.parse.quote(email, safe='')}" )

    # Attempt to delete should return 404
    r2 = client.delete(f"/activities/{act_quoted}/participants?email={urllib.parse.quote(email, safe='')}")
    assert r2.status_code == 404
