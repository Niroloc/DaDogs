import logging
import sqlite3
import os.path

from config.constants import DB_FILE, MIGRATION_FOLDER, LOGS


def do_setup():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    os.makedirs(MIGRATION_FOLDER, exist_ok=True)
    for file in os.listdir(MIGRATION_FOLDER):
        with open(os.path.join(MIGRATION_FOLDER, file), 'r') as f:
            queries = f.read().split(";")
            for query in queries:
                cur.execute(query)
    conn.commit()

if __name__ == '__main__' and not os.path.isfile(DB_FILE):
    logging.basicConfig(
        level=logging.INFO,
        filename=LOGS,
        format="%(pathname)s -- %(asctime)s -- [%(levelname)s] -- \"%(message)s \"")
