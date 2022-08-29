from dotenv import load_dotenv
import sqlite3
import pymssql
import os
import gui_for_message
from gui_for_tray_icon import TrayIcon


load_dotenv()


# Run tray-icon GUI
gui_tray = TrayIcon()
gui_tray.run_detached()


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


class MsSql:
    def __init__(self):
        try:
            # Connection for mssql
            self.msSqlCon = pymssql.connect(
                host=os.getenv('MSSQL_HOST'),
                user=os.getenv('MSSQL_USER'),
                password=os.getenv('MSSQL_PASSWORD'),
                database=os.getenv('MSSQL_db')
            )
        except:
            gui_messenger = gui_for_message.tk_gui()
            gui_messenger.dialog(
                'button_3.png',
                gui_tray.stop,
                True,
                None,
                None,
                'ارتباط با بانک اطلاعاتی با مشکل مواجه شد لطفا اتصالات را برسی کنید\nو برنامه را مجدد باز کنید'
            )
        # Create a dic and move data to it
        self.ms_cur = self.msSqlCon.cursor(as_dict=True)

    def execute(self, sql):
        self.ms_cur.execute(sql)

    def fetch(self):
        return self.ms_cur

    def close(self):
        self.msSqlCon.close()


# Create table in sqlite for save pay-log
try:
    sqlite = SqliteDb()
    sqlite.execute('''
    CREATE TABLE Pay(
        id INT NOT NULL,
        price INT NOT NULL,
        status INT NOT NULL
    );
    ''')
    sqlite.execute('''
    INSERT INTO pay(
            id, price, status
        )VALUES(
            0, 0, 0
        );
    ''')
    sqlite.commit()
    sqlite.close()
except:
    pass