from __future__ import annotations

import sys
import os
import sqlite3
from src.logger import logging
from src.exception import MyException
from langgraph.checkpoint.sqlite import SqliteSaver
from entity.config_entity import CheckpointerConfig


class SQLiteCheckpointer:
    def __init__(self, config: CheckpointerConfig):
        try:
            logging.info(f"Initializing SQLiteCheckpointer — db_path={config.db_path}")
            os.makedirs(os.path.dirname(config.db_path), exist_ok=True)
            self.conn = sqlite3.connect(
                database=config.db_path,
                check_same_thread=False,
            )
            self.checkpointer = SqliteSaver(conn=self.conn)
            logging.info("SQLiteCheckpointer initialized successfully")
        except Exception as e:
            raise MyException(e, sys)

    def get_checkpointer(self) -> SqliteSaver:
        return self.checkpointer

    def get_conn(self) -> sqlite3.Connection:
        return self.conn
