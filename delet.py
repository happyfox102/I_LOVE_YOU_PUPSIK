from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parent / "valentine.sqlite3"


def clear_database() -> None:
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        return

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = OFF")

        table_rows = conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
              AND name NOT LIKE 'sqlite_%'
            """
        ).fetchall()

        table_names = [row[0] for row in table_rows]
        if not table_names:
            print("No user tables found.")
            return

        for table_name in table_names:
            conn.execute(f'DELETE FROM "{table_name}"')

        conn.execute("DELETE FROM sqlite_sequence")
        conn.commit()

    print("Database cleared.")
    print("Tables:", ", ".join(table_names))


if __name__ == "__main__":
    clear_database()
