import sqlite3
import logging
from traceback import format_exc

from src.config.constants import DB_FILE


class Db:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.cur = self.conn.cursor()

    def get_dogs(self) -> list[tuple[int, str]]:
        query = '''
            select d.id, d.name, max(w.dt) as dt
            from dogs d left join walks w on d.id = w.dog_id
            where d.deleted = 0
            group by d.id, d.name
            order by dt desc, name asc
        '''
        self.cur.execute(query)
        res = self.cur.fetchall()
        return [(ident, name) for ident, name, _ in res]

    def add_dog(self, name) -> int:
        query = f'''
            insert into dogs
            (name)
            values
            ('{name}')
            returning id
        '''
        try:
            self.cur.execute(query)
            res = self.cur.fetchone()
            self.conn.commit()
            return res[0]
        except:
            logging.error("Inserting new dog finished with an error")
            logging.error(format_exc())
            return -1

    def delete_dog(self, ident):
        pass
