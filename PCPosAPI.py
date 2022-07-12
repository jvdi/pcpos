from time import sleep
from dotenv import load_dotenv
import os
import requests
import pymssql
import sqlite3


load_dotenv()


# Connectiton for sqlite
sqliteCon = sqlite3.connect('db/database.sqlite3')
sqlite_cur = sqliteCon.cursor()


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


# Connection for mssql
msSqlCon = pymssql.connect(
    host=os.getenv('MSSQL_HOST'),
    user=os.getenv('MSSQL_USER'),
    password=os.getenv('MSSQL_PASSWORD'),
    database=os.getenv('MSSQL_db')
)
# Get data from db and write to a dictionary
ms_cur = msSqlCon.cursor(as_dict=True)


while True:
    sleep(3)

    # Get Row from mssql
    # Exist Row: RowID, Fix_Acc1_ID, Fix_Acc2Type_ID, BedPrice, RowDesc
    ms_cur.execute('''
    SELECT * FROM DocD
    WHERE Fix_Acc1_ID=5 AND Fix_Acc2Type_ID=2 AND Acc2RowID=2
    ORDER BY RowID DESC;
    ''')

    # Get price and document id from mssql
    for i in ms_cur:
        global price_to_send, doch_id
        price_to_send = (int(i['BedPrice'])*10)
        doch_id = i['DocH_ID']
        # print(price_to_send)
        break

    # Set data for sending to pay-terminal
    data = {
        "DeviceIp": os.getenv('DEVICE_IP'),
        "DevicePort": os.getenv('DEVICE_PORT'),
        "ConnectionType": os.getenv('CONNECTION_TYPE'),
        "Amount": price_to_send,
        "AdvertisementData": doch_id,
        "OrderId": "90000",
        "SaleId": "0213541",
        "RetryTimeOut": "5000,5000,5000",
        "ResponseTimeout": "180000,5000,5000"
    }

    # Get last sent-pay
    sqlite_cur.execute('''
    SELECT * FROM pay ORDER BY id DESC;
    ''')
    last_pay_record = sqlite_cur.fetchone()
    print(doch_id, ',,,', last_pay_record[0])
    if (last_pay_record[0] != doch_id):
        req = requests.post(
            'http://'+os.getenv('REST_SERVER_IP')+':8050/api/Sale', json=data)

        json = req.json()

        # Show result in terminal
        for key in json:
            value = json[key]
            print(key, ' : ', value)

        # Save result in sqlite pay table
        sqlite_cur.execute('''
        INSERT INTO pay(
            id, price, status
        )VALUES(
            {}, {}, {}
        )
        '''.format(doch_id, price_to_send, json['PcPosStatusCode']))
        sqliteCon.commit()

    # Close all database
    # msSqlCon.close()
    # sqlite_cur.close()