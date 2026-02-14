import sqlite3
from pathlib import Path
from typing import Optional


DB_PATH = Path(__file__).resolve().parent / "valentine.sqlite3"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS love_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signed_at TEXT NOT NULL,
                hold_seconds REAL NOT NULL,
                note TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS button_clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clicked_at TEXT NOT NULL,
                action_label TEXT NOT NULL,
                sticker TEXT,
                photo_src TEXT
            )
            """
        )
        conn.commit()


def save_signature(hold_seconds: float, note: Optional[str] = None) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO love_documents (signed_at, hold_seconds, note)
            VALUES (datetime('now'), ?, ?)
            """,
            (hold_seconds, note),
        )
        conn.commit()
        return int(cursor.lastrowid)


def get_last_signature() -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, signed_at, hold_seconds, note
            FROM love_documents
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "signed_at": row["signed_at"],
        "hold_seconds": row["hold_seconds"],
        "note": row["note"],
    }


def save_button_click(
    action_label: str, sticker: Optional[str] = None, photo_src: Optional[str] = None
) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO button_clicks (clicked_at, action_label, sticker, photo_src)
            VALUES (datetime('now'), ?, ?, ?)
            """,
            (action_label, sticker, photo_src),
        )
        conn.commit()
        return int(cursor.lastrowid)
