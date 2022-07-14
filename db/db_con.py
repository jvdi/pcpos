import pymssql
import sqlite3
from dotenv import load_dotenv
import os


load_dotenv()


# Connectiton for sqlite
sqliteCon = sqlite3.connect('db/database.sqlite3')
sqlite_cur = sqliteCon.cursor()


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
    sqlite_cur.execute('''
    CREATE TABLE Pay(
        id INT NOT NULL,
        price INT NOT NULL,
        status INT NOT NULL
    );
    ''')
    print('Pay Tables -> Created')
except:
    print('Pay Tables -> Exist')
