# -*- coding: utf-8 -*-

from db.db_con import *
from gui_for_message import tk_gui
import os
from dotenv import load_dotenv
from time import sleep
import requests
import json as jsn


load_dotenv()


# Flag for process Control
run_flag = True

# Process
while run_flag:
    sleep(3)  # Witing time for check ms-db

    # Get Row from mssql
    # Exist Column: RowID, Fix_Acc1_ID, Fix_Acc2Type_ID, BedPrice, RowDesc, ...
    ms_cur = MsSql()
    ms_cur.execute('''
    SELECT * 
    FROM DocD
    WHERE Fix_Acc1_ID=5 AND Fix_Acc2Type_ID=2 AND (Acc2RowID=2 OR Acc2RowID=3)
    ORDER BY RowID DESC;
    ''')

    # Get price and document id from mssql
    for row in ms_cur.fetch():
        global price_to_send, doch_id, acc_number
        price_to_send = (int(row['BedPrice'])*10)
        doch_id = row['DocH_ID']
        acc_number = row['Acc2RowID']  # 2-> Sadad & 3-> Top
        break

    ms_cur.close()

    # Sadad transAction
    if acc_number == 2 and price_to_send != 0:
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
    # Pec transAction
    elif acc_number == 3 and price_to_send != 0:
        pec_service_api_dir = os.getenv('PEC_API_DIR')

        # Init Status
        stat = 'بدون وضعیت'
        stat_flg = True

        # Check for install service
        if not os.path.exists(pec_service_api_dir):
            stat = 'سرویس تاپ نصب نیست'
            stat_flg = False
            pec_gui = tk_gui()
            pec_gui.dialog(
                'button_3.png',
                gui_tray.stop,
                True,
                None,
                None,
                stat+'\nلطفا سرویس را نصب کنید\nو برنامه را مجدد باز کنید'
            )

        # Get last sent-pay
        sqlite = SqliteDb()
        sqlite.execute('''
        SELECT * FROM pay ORDER BY rowid DESC;
        ''')
        last_pay_record_id = sqlite.fetchone()

        # Remove TransAction - if removed
        if last_pay_record_id[0] > doch_id:
            sqlite.execute('''
            DELETE FROM Pay WHERE id='{}';
            '''.format(last_pay_record_id[0]))
            sqlite.commit()
            # Close sqlite connection
            sqlite.close()
        # Do a new TransAction if it's a new
        elif last_pay_record_id[0] < doch_id:
            # Request file
            request_file = os.path.join(
                pec_service_api_dir+'request/', 'TransAction.txt'
            )

            # Write new TransAction request for send to pay-terminal
            def write_request():
                if os.path.exists(request_file):
                    os.remove(request_file)
                file = open(request_file, 'w')
                file.write(
                    'Amount={}\ntype={}\nIP={}\nport={}'.format(
                        price_to_send, os.getenv('PEC_CON_TYPE'), os.getenv(
                            'PEC_DEVICE_IP'), os.getenv('PEC_DEVICE_PORT')
                    )
                )
                file.close()

            # Check for sent transAction
            def check_for_sent():
                not_sent = True
                while(not_sent):
                    if(os.path.exists(request_file)):
                        pass
                    else:
                        not_sent = False
                        global stat
                        stat = 'درخواست ارسال شد'

            # Response file
            response_file = os.path.join(
                pec_service_api_dir+'response/', 'TransAction.txt'
            )

            # Check for receive response
            def check_for_receive():
                response_is_not_exits = True
                while(response_is_not_exits):
                    if(os.path.exists(response_file)):
                        response_is_not_exits = False
                        global stat
                        stat = 'نتیجه درخواست - آمد'
                    else:
                        pass

            # TransAction
            def do_trans_action():
                write_request()
                check_for_sent()
                check_for_receive()
            # Do TransAction
            do_trans_action()

            # For cancell TransAction
            not_cancel = True

            def abort_pay():
                global not_cancel
                not_cancel = False

            # Check response for resend or done the mission
            while(not_cancel):
                # know errors
                def error_message(r):
                    if r == '99':
                        return 'لغو توسط کاربر'
                    elif r == '51':
                        return 'عدم موجودی کافی'
                    elif r == '55':
                        return 'رمز نامعتبر است'
                    else:
                        return 'خطای ناشناخته'

                # Open response file
                file = open(response_file, 'r')
                # Read a line of file and close & remove it
                txt = file.readline()
                file.close()
                os.remove(response_file)

                # Get responseCode
                etxt = txt.split()
                result = etxt[2]

                # Success TransAction
                if result == '00':
                    break
                # Fail TransAction -> Show Error
                else:
                    json_text = '{ "PcPosStatusCode":"'+result+'", "PcPosStatus":"' + \
                        stat+'", "ResponseCodeMessage":"' + \
                        error_message(result)+'"}'
                    json = jsn.loads(json_text)
                    # Gui
                    pec_gui = tk_gui()
                    pec_gui.show_message(
                        do_trans_action, abort_pay, json, 'تاپ')

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