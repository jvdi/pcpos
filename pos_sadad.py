import os, requests
from .db.sqlite import SqliteDb
from gui_for_message import tk_gui
from dotenv import load_dotenv

load_dotenv()

def sadad(price_to_send, doch_id, gui_tray):
    # Set data for sending to pay-terminal
    data = {
        "DeviceIp": os.getenv('SADAD_DEVICE_IP'),
        "DevicePort": os.getenv('SADAD_DEVICE_PORT'),
        "ConnectionType": os.getenv('SADAD_CON_TYPE'),
        "DeviceType": os.getenv('SADAD_DEVICE_TYPE'),
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

    # Remove TransAction
    if last_pay_record_id[0] > doch_id:
        sqlite.execute('''
        DELETE FROM Pay WHERE id='{}';
        '''.format(last_pay_record_id[0]))
        sqlite.commit()
        # Close sqlite connection
        sqlite.close()
    # Do a new TransAction
    elif last_pay_record_id[0] < doch_id:
        # Send request to pay-terminal
        def send_prc():
            try:
                req = requests.post(
                    'http://'+os.getenv('SADAD_REST_API_IP')+':8050/api/Sale', json=data)
                global json
                json = req.json()
            except:
                req_gui = tk_gui()
                req_gui.dialog(
                    'button_3.png',
                    gui_tray.stop,
                    True,
                    None,
                    None,
                    'سرویس سداد با مشکل مواجه شد لطفا پیکربندی را کنترل کنید\nو برنامه را مجدد باز کنید'
                )
        send_prc()

        # For cancell pay
        not_cancel = True

        def abort_pay():
            global not_cancel
            not_cancel = False

        # Check response for resend or done the mission
        while(not_cancel):
            if json['PcPosStatusCode'] == 4 and json['ResponseCode'] == '00':
                break

            # Gui
            sadad_gui = tk_gui()
            sadad_gui.show_message(send_prc, abort_pay, json, 'سداد')

        # Show result in terminal
        print('********[Sadad]********')
        for key in json:
            value = json[key]
            print(key, ' : ', value)
        print('******[End-Sadad]******')

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