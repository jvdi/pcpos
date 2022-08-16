from db.db_con import *
from gui import show_message
import os
from dotenv import load_dotenv
from time import sleep
import requests


load_dotenv()


while True:
    sleep(3)  # Witing time for check ms-db

    # Get Row from mssql
    # Exist Column: RowID, Fix_Acc1_ID, Fix_Acc2Type_ID, BedPrice, RowDesc, ...
    ms_cur = MsSql()
    ms_cur.execute('''
    SELECT * 
    FROM DocD
    WHERE Fix_Acc1_ID=5 AND Fix_Acc2Type_ID=2 AND Acc2RowID=2
    ORDER BY RowID DESC;
    ''')

    # Get price and document id from mssql
    for row in ms_cur.fetch():
        global price_to_send, doch_id
        price_to_send = (int(row['BedPrice'])*10)
        doch_id = row['DocH_ID']
        break
    
    ms_cur.close()

    # Set data for sending to pay-terminal
    data = {
        "DeviceIp": os.getenv('DEVICE_IP'),
        "DevicePort": os.getenv('DEVICE_PORT'),
        "ConnectionType": os.getenv('CONNECTION_TYPE'),
        "DeviceType": "3",
        "Amount": price_to_send,
        "RetryTimeOut": "5000,5000,5000",
        "ResponseTimeout": "180000,5000,5000"
    }
    
    # Get last sent-pay
    sqlite = SqliteDb()
    sqlite.execute('''
    SELECT * FROM pay ORDER BY rowid DESC;
    ''')
    last_pay_record_id = sqlite.fetchone()

    if (last_pay_record_id[0] != doch_id):
        # Send request to pay-terminal
        def send_prc():
            req = requests.post(
                'http://'+os.getenv('REST_SERVER_IP')+':8050/api/Sale', json=data)
            global json
            json = req.json()
        
        send_prc()

        # For cancell pay
        flag = True
        def abort_pay():
            global flag
            flag = False

        # Check response for resend or done the mission
        while(flag):
            if json['PcPosStatusCode'] == 4 and json['ResponseCode'] == '00':
                break

            # Gui
            show_message(send_prc, abort_pay, json)

        # Show result in terminal
        for key in json:
            value = json[key]
            print(key, ' : ', value)

        # Save result in sqlite pay table
        sqlite.execute('''
        INSERT INTO pay(
            id, price, status
        )VALUES(
            {}, {}, {}
        )
        '''.format(doch_id, price_to_send, json['PcPosStatusCode']))
        sqlite.commit()
        
        # Close sqlite connection
        sqlite.close()