import sqlite3

class SqliteDb:
    def __init__(self):
        # Connectiton for sqlite
        self.sqlite_con = sqlite3.connect('db/database.sqlite3')
        self.sqlite_cur = self.sqlite_con.cursor()

    def execute(self, sql):
        self.sqlite_cur.execute(sql)

    def fetchone(self):
        return self.sqlite_cur.fetchone()

    def commit(self):
        self.sqlite_con.commit()

    def close(self):
        self.sqlite_cur.close()