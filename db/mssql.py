import pymssql, os, gui_for_message
from dotenv import load_dotenv

load_dotenv()

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
                lambda: [exit()],
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