import pymssql, os, gui_for_message
from .sqlite import SqliteDb
from dotenv import load_dotenv
from gui_for_tray_icon import TrayIcon

load_dotenv()

# Run tray-icon GUI
gui_tray = TrayIcon()
gui_tray.run_detached()

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
                lambda: [gui_tray.stop(), exit()],
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