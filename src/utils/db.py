import sqlite3

from src.config.constants import DB_FILE


class Db:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.cur = self.conn.cursor()

    def func(self):
        pass
