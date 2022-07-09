import pymssql
import sqlite3

# Connectiton for sqlite
sqliteCon = sqlite3.connect('db/database.sqlite3')
sqlite_cur = sqliteCon.cursor()


# Create table in sqlite for detail of mssql-connection
try:
    sqlite_cur.execute('''
    CREATE TABLE Connection(
        host     TEXT NOT NULL,
        user     TEXT NOT NULL,
        password TEXT NOT NULL,
        db_name  TEXT
    );
    ''')
    print('MSSQL Connection table is create.')
except:
    print('MSSQL Connection table is already created.')


# Create table in sqlite for save pay-log
try:
    sqlite_cur.execute('''
    CREATE TABLE Pay(
        id INT NOT NULL,
        price INT NOT NULL,
        status INT NOT NULL
    );
    ''')
    print('Pay Tables is Created.')
except:
    print('Pay Tables already Created.')

# Connect to MSSQL with connection detail from sqlite
sqlite_cur.execute('''
select * from `Connection`;
''')
record = sqlite_cur.fetchone()


# Connection for mssql
msSqlCon = pymssql.connect(
    host=record[0],
    user=record[1],
    password=record[2],
    database=record[3]
)
# Get data from db and write to a dictionary
ms_cur = msSqlCon.cursor(as_dict=True)
