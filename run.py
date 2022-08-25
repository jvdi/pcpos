# -*- coding: utf-8 -*-

from db.db_con import *
from gui import tk_gui
import os
from dotenv import load_dotenv
from time import sleep
import requests
import json as jsn


load_dotenv()


while True:
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

        if last_pay_record_id[0] > doch_id:
            sqlite.execute('''
            DELETE FROM Pay WHERE id='{}';
            '''.format(last_pay_record_id[0]))
            sqlite.commit()
            # Close sqlite connection
            sqlite.close()
        elif last_pay_record_id[0] < doch_id:
            # Send request to pay-terminal
            def send_prc():
                req = requests.post(
                    'http://'+os.getenv('SADAD_REST_API_IP')+':8050/api/Sale', json=data)
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
                gui = tk_gui()
                gui.show_message(send_prc, abort_pay, json, 'سداد')

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
        stat = 'بدون وضعیت'
        stat_flg = True
        filepath = os.path.join(
            'C:/Users/Public/PEC_PCPOS/request', 'TransAction.txt'
        )
        # Check for install service
        if not os.path.exists('C:/Users/Public/PEC_PCPOS/request'):
            stat = 'سرویس تاپ نصب نیست'
            stat_flg = False

        # Get last sent-pay
        sqlite = SqliteDb()
        sqlite.execute('''
        SELECT * FROM pay ORDER BY rowid DESC;
        ''')
        last_pay_record_id = sqlite.fetchone()

        if last_pay_record_id[0] > doch_id:
            sqlite.execute('''
            DELETE FROM Pay WHERE id='{}';
            '''.format(last_pay_record_id[0]))
            sqlite.commit()
            # Close sqlite connection
            sqlite.close()
        elif last_pay_record_id[0] < doch_id and stat_flg:
            # Check for come result
            def wait_for_result():
                response_is_not_exits = True
                trans_action_file = os.path.join('C:/Users/Public/PEC_PCPOS/response', 'TransAction.txt')
                while(response_is_not_exits):
                    if(os.path.exists(trans_action_file)):
                        response_is_not_exits = False
                        global stat
                        stat = 'نتیجه درخواست رسید'
                    else:
                        pass

            # Write TransAction for send to pay-terminal
            def send_prc():
                if os.path.exists('C:/Users/Public/PEC_PCPOS/response/TransAction.txt'):
                    os.remove('C:/Users/Public/PEC_PCPOS/response/TransAction.txt')
                file = open(filepath, 'w')
                file.write(
                    'Amount={}\ntype={}\nIP={}\nport={}'.format(
                        price_to_send, os.getenv('PEC_CON_TYPE'), os.getenv('PEC_DEVICE_IP'), os.getenv('PEC_DEVICE_PORT')
                    )
                )
                file.close()
                
                # Check for sent transAction status
                not_sent = True
                trans_action_file = os.path.join('C:/Users/Public/PEC_PCPOS/request', 'TransAction.txt')
                while(not_sent):
                    if(os.path.exists(filepath)):
                        pass
                    else:
                        not_sent = False
                        global stat
                        stat = 'درخواست ارسال شد'
                
                # Check for result is come?
                wait_for_result()

            send_prc()
            

            # For cancell pay
            flag = True

            def abort_pay():
                global flag
                flag = False

            # Check response for resend or done the mission
            while(flag):
                filepath_resp = os.path.join('C:/Users/Public/PEC_PCPOS/response', 'TransAction.txt')
                file = open(filepath_resp, 'r')
                
                txt = file.readline()
                etxt = txt.split()
                result = etxt[2]

                def error_message(r):
                    if r == '99':
                        return 'لغو توسط کاربر'
                    elif r == '51':
                        return 'عدم موجودی کافی'
                    elif r == '55':
                        return 'رمز نامعتبر است'
                    else:
                        return 'خطای ناشناخته'

                if result == '00':
                    file.close()
                    break
                else:
                    json_text = '{ "PcPosStatusCode":"'+result+'", "PcPosStatus":"'+stat+'", "ResponseCodeMessage":"'+error_message(result)+'"}'
                    json = jsn.loads(json_text)
                    file.close()
                    # Gui
                    gui = tk_gui()
                    gui.show_message(send_prc, abort_pay, json, 'تاپ')
            
            os.remove('C:/Users/Public/PEC_PCPOS/response/TransAction.txt')

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
        elif last_pay_record_id[0] < doch_id and stat_flg == False:
            print(stat, ' - ', stat_flg)