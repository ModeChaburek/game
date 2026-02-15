import os
import sqlite3
import settings


def _connect():
    db_path = settings.DB_PATH
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return sqlite3.connect(db_path)


def init_db():
    conn = _connect()
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS game_results ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, "
            "player1 TEXT NOT NULL, "
            "player2 TEXT NOT NULL, "
            "score1 INTEGER NOT NULL, "
            "score2 INTEGER NOT NULL"
            ")"
        )
        conn.commit()
    finally:
        conn.close()


def add_game_result(player1, player2, score1, score2):
    init_db()
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO game_results (player1, player2, score1, score2) VALUES (?, ?, ?, ?)",
            (player1, player2, int(score1), int(score2))
        )
        conn.commit()
    finally:
        conn.close()


def get_latest_results(limit=10):
    init_db()
    conn = _connect()
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(
            "SELECT player1, player2, score1, score2, created_at FROM game_results ORDER BY id DESC LIMIT ?",
            (int(limit),)
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
