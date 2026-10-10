from app.errors import AppError
from app.providers.mock import MockLLMProvider
from app.services.sessions import get_session, update_phase


llm = MockLLMProvider()


def configure_llm(provider) -> None:
    global llm
    llm = provider


def generate_report(session_id: str):
    session = get_session(session_id)
    if session.phase not in ("ended", "report_ready"):
        raise AppError("Report is available only after the discussion ends", 400)
    report = llm.feedback_report(session.id, session.topic, session.transcript)
    update_phase(session_id, "report_ready")
    return report
