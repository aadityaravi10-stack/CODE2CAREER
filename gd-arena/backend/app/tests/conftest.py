import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.environ["DATABASE_URL"] = f"sqlite:///{ROOT / 'test_gd_arena.sqlite3'}"

from app.db import database  # noqa: E402

database.DB_PATH = str(ROOT / "test_gd_arena.sqlite3")


def reset_db():
    db_path = Path(database.DB_PATH)
    if db_path.exists():
        db_path.unlink()


def client():
    reset_db()
    from app.main import create_app

    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()
