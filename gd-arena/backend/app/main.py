from __future__ import annotations

from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, request

from app.db.database import init_db
from app.errors import AppError
from app.models.schemas import CreateSessionRequest, StudentTurnRequest
from app.providers.real import ProviderRegistry
from app.services.reports import configure_llm as configure_report_llm, generate_report
from app.services.sessions import add_ai_turn, add_student_turn, configure_llm as configure_session_llm, create_session, end_session, get_session
from app.services.topics import list_topics, resolve_topic


def to_jsonable(value):
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    return value


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)
    init_db()
    providers = ProviderRegistry()
    configure_session_llm(providers.llm())
    configure_report_llm(providers.llm())

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        return response

    @app.route("/", defaults={"path": ""}, methods=["OPTIONS"])
    @app.route("/<path:path>", methods=["OPTIONS"])
    def options(path: str):
        return make_response("", 204)

    @app.errorhandler(AppError)
    def app_error(error: AppError):
        payload = {"detail": error.message}
        if error.hint:
            payload["hint"] = error.hint
        return jsonify(payload), error.status_code

    @app.errorhandler(Exception)
    def unhandled_error(error: Exception):
        return (
            jsonify(
                {
                    "detail": "Something went wrong in GD Arena API.",
                    "hint": "The demo is designed to keep working in mock mode. Try again or restart the backend.",
                }
            ),
            500,
        )

    @app.get("/health")
    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "mode": providers.selected_name(), "server": "Flask WSGI"})

    @app.get("/topics")
    @app.get("/api/topics")
    def topics():
        return jsonify(to_jsonable(list_topics()))

    @app.post("/sessions")
    @app.post("/api/sessions")
    def sessions():
        payload = CreateSessionRequest(**(request.get_json(silent=True) or {}))
        topic = resolve_topic(payload.topic_id, payload.custom_topic)
        return jsonify(
            to_jsonable(
                create_session(
                    topic,
                    difficulty=payload.difficulty,
                    language=payload.language,
                    duration_minutes=payload.duration_minutes,
                    practice_mode=payload.practice_mode,
                )
            )
        )

    @app.get("/sessions/<session_id>")
    @app.get("/api/sessions/<session_id>")
    def session_detail(session_id: str):
        return jsonify(to_jsonable(get_session(session_id)))

    @app.post("/sessions/<session_id>/student-turn")
    @app.post("/api/sessions/<session_id>/student-turn")
    def student_turn(session_id: str):
        payload = StudentTurnRequest(**(request.get_json(silent=True) or {}))
        return jsonify(to_jsonable(add_student_turn(session_id, payload.text)))

    @app.post("/sessions/<session_id>/ai-turn")
    @app.post("/api/sessions/<session_id>/ai-turn")
    def ai_turn(session_id: str):
        session, message, next_speaker = add_ai_turn(session_id)
        return jsonify(
            to_jsonable(
                {
                    "session": session,
                    "message": message,
                    "next_speaker": next_speaker,
                }
            )
        )

    @app.post("/sessions/<session_id>/end")
    @app.post("/api/sessions/<session_id>/end")
    def end(session_id: str):
        return jsonify(to_jsonable(end_session(session_id)))

    @app.get("/sessions/<session_id>/report")
    @app.get("/api/sessions/<session_id>/report")
    def report(session_id: str):
        return jsonify(to_jsonable(generate_report(session_id)))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True, threaded=True)
