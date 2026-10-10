import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = BASE_DIR / "gd_arena.sqlite3"


def _path_from_url(database_url: str | None = None) -> str:
    if os.getenv("VERCEL"):
        return "/tmp/gd_arena.sqlite3"
    url = database_url or os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
    if url == "sqlite:///:memory:":
        return ":memory:"
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "", 1)
    return str(DEFAULT_DB_PATH)


DB_PATH = _path_from_url()


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    if DB_PATH != ":memory:":
        Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                phase TEXT NOT NULL,
                created_at TEXT NOT NULL,
                demo_mode INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS transcript_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                speaker TEXT NOT NULL,
                source TEXT NOT NULL,
                text TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );
            """
        )
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(sessions)").fetchall()}
        migrations = {
            "difficulty": "ALTER TABLE sessions ADD COLUMN difficulty TEXT NOT NULL DEFAULT 'balanced'",
            "language": "ALTER TABLE sessions ADD COLUMN language TEXT NOT NULL DEFAULT 'en-IN'",
            "duration_minutes": "ALTER TABLE sessions ADD COLUMN duration_minutes INTEGER NOT NULL DEFAULT 8",
            "practice_mode": "ALTER TABLE sessions ADD COLUMN practice_mode INTEGER NOT NULL DEFAULT 1",
        }
        for column, statement in migrations.items():
            if column not in columns:
                conn.execute(statement)
