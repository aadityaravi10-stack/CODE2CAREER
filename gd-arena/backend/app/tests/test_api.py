from app.tests.conftest import client


def test_health_endpoint():
    c = client()
    response = c.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_session_creation():
    c = client()
    response = c.post("/sessions", json={"topic_id": "ai-education", "panel_size": 3})
    assert response.status_code == 200
    data = response.get_json()
    assert data["phase"] == "opening"
    assert data["demo_mode"] is True
    assert data["transcript"][0]["speaker"] == "Moderator"


def test_session_keeps_room_settings():
    c = client()
    response = c.post(
        "/sessions",
        json={"topic_id": "ai-education", "difficulty": "challenging", "language": "hi-IN", "duration_minutes": 5},
    )
    data = response.get_json()
    assert data["difficulty"] == "challenging"
    assert data["language"] == "hi-IN"
    assert data["duration_minutes"] == 5


def test_student_turn_transcript_insertion():
    c = client()
    session = c.post("/sessions", json={"topic_id": "remote-work"}).get_json()
    response = c.post(f"/sessions/{session['id']}/student-turn", json={"text": "Remote work saves commute time."})
    assert response.status_code == 200
    assert any(m["source"] == "student" and "commute" in m["text"] for m in response.get_json()["transcript"])


def test_mock_ai_turn_generation():
    c = client()
    session = c.post("/sessions", json={"topic_id": "remote-work"}).get_json()
    c.post(f"/sessions/{session['id']}/student-turn", json={"text": "Remote work helps productivity."})
    response = c.post(f"/sessions/{session['id']}/ai-turn")
    assert response.status_code == 200
    assert response.get_json()["message"]["source"] == "ai"
    assert response.get_json()["message"]["speaker"] in {"Riya", "Arjun", "Meera"}


def test_report_generation_with_transcript_quotes():
    c = client()
    session = c.post("/sessions", json={"topic_id": "ai-education"}).get_json()
    c.post(f"/sessions/{session['id']}/student-turn", json={"text": "AI can personalize practice for students."})
    c.post(f"/sessions/{session['id']}/student-turn", json={"text": "But schools need safeguards and teacher oversight."})
    c.post(f"/sessions/{session['id']}/end")
    report = c.get(f"/sessions/{session['id']}/report")
    assert report.status_code == 200
    sections = report.get_json()["sections"]
    quotes = [value["quote"] for value in sections.values() if value["quote"]]
    assert "AI can personalize practice for students." in quotes
    assert "But schools need safeguards and teacher oversight." in quotes
    assert 1 <= report.get_json()["overall_score"] <= 10
    assert report.get_json()["rating"] in {"Weak", "Average", "Strong", "Elite"}


def test_report_does_not_invent_quotes_when_insufficient():
    c = client()
    session = c.post("/sessions", json={"topic_id": "ai-education"}).get_json()
    c.post(f"/sessions/{session['id']}/end")
    report = c.get(f"/sessions/{session['id']}/report")
    assert report.status_code == 200
    sections = report.get_json()["sections"]
    assert all(section["quote"] is None for section in sections.values())


def test_report_before_end_fails():
    c = client()
    session = c.post("/sessions", json={"topic_id": "ai-education"}).get_json()
    response = c.get(f"/sessions/{session['id']}/report")
    assert response.status_code == 400
