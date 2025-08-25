import datetime
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

    def delete_dog(self, ident: int) -> None:
        query = f'''
            update dogs
            set deleted = 1
            where id = {ident}
        '''
        self.cur.execute(query)
        self.conn.commit()

    def add_walk(self, ident: int, dt: datetime.date, ts: datetime.time, quantity: int) -> int:
        query = f'''
            insert into walks
            (dt, ts, quantity, dog_id)
            values
            ('{dt.strftime("%Y-%m-%d")}', '{ts.strftime("%H:%M:%S")}', {quantity}, {ident})
            returning id
        '''
        self.cur.execute(query)
        res = self.cur.fetchall()
        self.conn.commit()
        if len(res) <= 0:
            logging.error(format_exc())
            return -1
        return res[0][0]

    def get_walks(self, month: int = None) -> list[tuple[str, str, int]]:
        today = datetime.date.today()
        query: str
        if month is None:
            query = f'''
                select w.ts, d.name, w.quantity
                from walks w left join dogs d on d.id = w.dog_id
                where w.dt = '{today.strftime("%Y-%m-%d")}'
                order by w.ts
            '''
        else:
            query = f'''
                        select w.ts, d.name, w.quantity
                        from walks w left join dogs d on d.id = w.dog_id
                        where strftime('%m', datetime(w.dt)) = '{month}'
                        order by w.ts
                    '''
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_dog_name_from_id(self, ident: int) -> str:
        query = f'''
            select name
            from dogs
            where id = {ident}
        '''
        self.cur.execute(query)
        res = self.cur.fetchall()
        if len(res) <= 0:
            logging.error(format_exc())
            return ""
        return res[0][0]

    def get_amounts_by_dogs(self) -> list[tuple[str, int, int]]:
        query = '''
            select d.name, sum(w.quantity) as summ, count(w.quantity) as count
            from walks w left join dogs d on w.dog_id = d.id
            group by d.name
            order by summ desc
        '''
        self.cur.execute(query)
        return self.cur.fetchall()
