# -*- coding: utf-8 -*-

from .db.mssql import MsSql
from .db.sqlite import SqliteDb
from pos_sadad import sadad
from pos_pec import pec
from pos_asanp import asanp
from gui_for_tray_icon import TrayIcon
import os, time
from dotenv import load_dotenv

load_dotenv()

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

# Wait for load sql - or check to load
time.sleep(int(os.getenv('DB_WAIT_TIME')))

# Run tray-icon GUI
gui_tray = TrayIcon()
gui_tray.run_detached()

# Flag for process Control - For Stop app
run_flag = True

# run_flag is set in db_con file
# Main process of app
while run_flag:
    time.sleep(int(os.getenv('CHECK_TIME')))  # Witing time for check ms-db to get new TransAction

    # Start a connection to mssql server
    ms_cur = MsSql()

    # Get Row from mssql
    # Exist Column: RowID, Fix_Acc1_ID, Fix_Acc2Type_ID, BedPrice, RowDesc, ...
    ms_cur.execute('''
    SELECT * 
    FROM DocD
    WHERE Fix_Acc1_ID=5 AND Fix_Acc2Type_ID=2 AND (Acc2RowID='''+os.getenv('SADAD_ACC_ID')+''' OR Acc2RowID='''+os.getenv('PEC_ACC_ID')+''' OR Acc2RowID='''+os.getenv('ASAN-P_ACC_ID')+''')
    ORDER BY RowID DESC;
    ''')

    # Get price and document id from mssql and save to Gloabal var
    for row in ms_cur.fetch():
        global price_to_send, doch_id, acc_number
        price_to_send = (int(row['BedPrice']) * int(os.getenv('PRICE_FACTOR')))
        doch_id = row['DocH_ID']
        acc_number = row['Acc2RowID']
        break

    # Close connection of mssql
    ms_cur.close()

    # Do Sadad transAction
    if (str(os.getenv('SADAD_RUN')) == 'YES') and acc_number == int(os.getenv('SADAD_ACC_ID')) and price_to_send != 0:
        # Send to sadad and get result
        sadad(price_to_send, doch_id, gui_tray)
    # Pec transAction
    elif (str(os.getenv('PEC_RUN')) == 'YES') and acc_number == int(os.getenv('PEC_ACC_ID')) and price_to_send != 0:
        # Send price to PEC
        pec(doch_id, price_to_send, gui_tray)
    # Asan-P transAction
    elif (str(os.getenv('ASAN-P_RUN')) == 'YES') and acc_number == int(os.getenv('ASAN-P_ACC_ID')) and price_to_send != 0:
        # Send price to asanpardakht
        asanp(doch_id, price_to_send)