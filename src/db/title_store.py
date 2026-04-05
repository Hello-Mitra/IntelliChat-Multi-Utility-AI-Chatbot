from __future__ import annotations

import sys
import sqlite3
from src.logger import logging
from src.exception import MyException


class TitleStore:
    """Manages conversation titles in a dedicated SQLite table."""

    def __init__(self, conn: sqlite3.Connection):
        try:
            logging.info("Initializing TitleStore")
            self.conn = conn
            self._init_table()
            logging.info("TitleStore initialized successfully")
        except Exception as e:
            raise MyException(e, sys)

    def _init_table(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS thread_titles (
                thread_id TEXT PRIMARY KEY,
                title     TEXT
            )
        """)
        self.conn.commit()

    def save(self, thread_id: str, title: str) -> None:
        """Insert or replace a title for a given thread."""
        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO thread_titles (thread_id, title) VALUES (?, ?)",
                (thread_id, title),
            )
            self.conn.commit()
            logging.info(f"Title saved for thread {thread_id}: {title}")
        except Exception as e:
            raise MyException(e, sys)

    def get_all(self) -> dict[str, str]:
        """Return {thread_id: title} for all saved threads."""
        try:
            cursor = self.conn.execute("SELECT thread_id, title FROM thread_titles")
            return {row[0]: row[1] for row in cursor.fetchall()}
        except Exception as e:
            raise MyException(e, sys)
