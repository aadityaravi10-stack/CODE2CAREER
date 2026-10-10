from datetime import datetime, timezone
from uuid import uuid4

from app.db.database import get_connection
from app.errors import AppError
from app.models.schemas import SessionResponse, TranscriptMessage
from app.providers.mock import MockLLMProvider, PARTICIPANTS
from app.state.moderator import ModeratorStateMachine


llm = MockLLMProvider()
moderator = ModeratorStateMachine()


def configure_llm(provider) -> None:
    global llm
    llm = provider


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_message(row) -> TranscriptMessage:
    return TranscriptMessage(
        id=row["id"],
        session_id=row["session_id"],
        speaker=row["speaker"],
        source=row["source"],
        text=row["text"],
        timestamp=datetime.fromisoformat(row["timestamp"]),
    )


def get_session(session_id: str) -> SessionResponse:
    with get_connection() as conn:
        session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not session:
            raise AppError("Session not found", 404)
        rows = conn.execute(
            "SELECT * FROM transcript_messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,),
        ).fetchall()
    return SessionResponse(
        id=session["id"],
        topic=session["topic"],
        phase=session["phase"],
        created_at=datetime.fromisoformat(session["created_at"]),
        demo_mode=bool(session["demo_mode"]),
        difficulty=session["difficulty"],
        language=session["language"],
        duration_minutes=session["duration_minutes"],
        practice_mode=bool(session["practice_mode"]),
        transcript=[_row_to_message(row) for row in rows],
    )


def create_session(
    topic: str,
    difficulty: str = "balanced",
    language: str = "en-IN",
    duration_minutes: int = 8,
    practice_mode: bool = True,
) -> SessionResponse:
    session_id = str(uuid4())
    created_at = _now_iso()
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO sessions
            (id, topic, phase, created_at, demo_mode, difficulty, language, duration_minutes, practice_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (session_id, topic, "opening", created_at, 1, difficulty, language, duration_minutes, int(practice_mode)),
        )
    add_message(session_id, "Moderator", "moderator", llm.moderator_message(topic, "opening", [], language))
    return get_session(session_id)


def add_message(session_id: str, speaker: str, source: str, text: str) -> TranscriptMessage:
    if not text or not text.strip():
        raise AppError("Message text cannot be empty", 400)
    timestamp = _now_iso()
    with get_connection() as conn:
        exists = conn.execute("SELECT id FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not exists:
            raise AppError("Session not found", 404)
        cursor = conn.execute(
            """
            INSERT INTO transcript_messages (session_id, speaker, source, text, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, speaker, source, text.strip(), timestamp),
        )
        row = conn.execute("SELECT * FROM transcript_messages WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _row_to_message(row)


def update_phase(session_id: str, phase: str) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE sessions SET phase = ? WHERE id = ?", (phase, session_id))


def add_student_turn(session_id: str, text: str) -> SessionResponse:
    message = add_message(session_id, "You", "student", text)
    session = get_session(session_id)
    new_phase = moderator.next_after_student_turn(session.phase, session.transcript)
    if new_phase != session.phase:
        update_phase(session_id, new_phase)
        if new_phase == "closing_round":
            add_message(session_id, "Moderator", "moderator", llm.moderator_message(session.topic, "closing_round", session.transcript, session.language))
    return get_session(session_id)


def add_ai_turn(session_id: str) -> tuple[SessionResponse, TranscriptMessage, str | None]:
    session = get_session(session_id)
    if session.phase in ("ended", "report_ready"):
        raise AppError("Discussion has ended", 400)
    ai_count = len([m for m in session.transcript if m.source == "ai"])
    participant = PARTICIPANTS[ai_count % len(PARTICIPANTS)]
    text = llm.participant_turn(participant, session.topic, session.transcript, session.phase, session.language)
    message = add_message(session_id, participant["name"], "ai", text)
    session = get_session(session_id)
    new_phase = moderator.next_after_ai_turn(session.phase, session.transcript)
    if new_phase == "ended":
        update_phase(session_id, "ended")
        add_message(session_id, "Moderator", "moderator", llm.moderator_message(session.topic, "ended", session.transcript, session.language))
    updated = get_session(session_id)
    next_name = PARTICIPANTS[(ai_count + 1) % len(PARTICIPANTS)]["name"] if updated.phase != "ended" else None
    return updated, message, next_name


def end_session(session_id: str) -> SessionResponse:
    session = get_session(session_id)
    if session.phase not in ("ended", "report_ready"):
        update_phase(session_id, "ended")
        add_message(session_id, "Moderator", "moderator", llm.moderator_message(session.topic, "ended", session.transcript, session.language))
    return get_session(session_id)
