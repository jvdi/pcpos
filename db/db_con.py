import pymssql
import sqlite3
from dotenv import load_dotenv
import os


load_dotenv()

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

# Connection for mssql
msSqlCon = pymssql.connect(
    host=os.getenv('MSSQL_HOST'),
    user=os.getenv('MSSQL_USER'),
    password=os.getenv('MSSQL_PASSWORD'),
    database=os.getenv('MSSQL_db')
)
ms_cur = msSqlCon.cursor(as_dict=True)  # Create a dic and move data to it


# Create table in sqlite for save pay-log
try:
    sqlite = SqliteDb()
    sqlite.lite_exec('''
    CREATE TABLE Pay(
        id INT NOT NULL,
        price INT NOT NULL,
        status INT NOT NULL
    );
    ''')
    print('Pay Tables -> Created')
    sqlite.lite_close()
except:
    print('Pay Tables -> Exist')
