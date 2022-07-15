from db.db_con import *
import os
from dotenv import load_dotenv
from time import sleep
import requests
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage

# asset directory
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


load_dotenv()


while True:
    sleep(3)  # Witing time for check ms-db

    # Get Row from mssql
    # Exist Column: RowID, Fix_Acc1_ID, Fix_Acc2Type_ID, BedPrice, RowDesc, ...
    ms_cur.execute('''
    SELECT * 
    FROM DocD
    WHERE Fix_Acc1_ID=5 AND Fix_Acc2Type_ID=2 AND Acc2RowID=2
    ORDER BY RowID DESC;
    ''')

    # Get price and document id from mssql
    for row in ms_cur:
        global price_to_send, doch_id
        price_to_send = (int(row['BedPrice'])*10)
        doch_id = row['DocH_ID']
        break

    # Set data for sending to pay-terminal
    data = {
        "DeviceIp": os.getenv('DEVICE_IP'),
        "DevicePort": os.getenv('DEVICE_PORT'),
        "ConnectionType": os.getenv('CONNECTION_TYPE'),
        "DeviceType": "3",
        "Amount": price_to_send,
        # "AdvertisementData": doch_id,
        # "OrderId": "90000",
        # "SaleId": "0213541",
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
            window = Tk()
            window.title('PCPos')
            window.iconbitmap('assets/pos.ico')
            window.eval('tk::PlaceWindow . center')
            window.geometry("300x150")
            window.configure(bg = "#FFFFFF")
            window.resizable(False, False)
            window.attributes('-topmost',True)

            canvas = Canvas(
            window,
            bg = "#FFFFFF",
            height = 150,
            width = 300,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
            )
            # run
            canvas.place(x = 0, y = 0)
            button_image_1 = PhotoImage(
                file=relative_to_assets("button_1.png"))
            button_1 = Button(
                image=button_image_1,
                borderwidth=0,
                highlightthickness=0,
                command=lambda: [window.destroy(), send_prc()],
                relief="flat"
            )
            button_1.place(
                x=7.0,
                y=89.0,
                width=90.0,
                height=46.0
            )
            # cancell
            button_image_2 = PhotoImage(
                file=relative_to_assets("button_2.png"))
            button_2 = Button(
                image=button_image_2,
                borderwidth=0,
                highlightthickness=0,
                command=lambda: [window.destroy() , abort_pay()],
                relief="flat"
            )
            button_2.place(
                x=203.0,
                y=89.0,
                width=90.0,
                height=46.0
            )

            entry_image_1 = PhotoImage(
                file=relative_to_assets("entry_1.png"))
            entry_bg_1 = canvas.create_image(
                150.0,
                37.5,
                image=entry_image_1
            )
            entry_1 = Text(
                bd=0,
                bg="#C4C4C4",
                highlightthickness=0,
                font=("Aria", 15),
                wrap='word',


            )
            entry_1.place(
                x=0.0,
                y=0.0,
                width=300.0,
                height=73.0
            )
            # Print error for user
            entry_1.insert("end", json['PcPosStatus']+'\n'+json['ResponseCodeMessage'])
            window.mainloop()

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
        
        # Close all database
        sqlite.close()

    # msSqlCon.close()
