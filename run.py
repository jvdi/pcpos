# -*- coding: utf-8 -*-

from db.db_con import *
from gui_for_message import tk_gui
import os, time, requests
from dotenv import load_dotenv
import json as jsn
import clr, re

# For dotnet dll
clr.AddReference("module/PosInterface")
from PosInterface import PCPos
from System import DateTime

load_dotenv()

# Wait for load sql - or check to load
time.sleep(int(os.getenv('DB_WAIT_TIME')))

# Process
while run_flag:
    time.sleep(int(os.getenv('CHECK_TIME')))  # Witing time for check ms-db

    # Get Row from mssql
    # Exist Column: RowID, Fix_Acc1_ID, Fix_Acc2Type_ID, BedPrice, RowDesc, ...
    ms_cur = MsSql()
    ms_cur.execute('''
    SELECT * 
    FROM DocD
    WHERE Fix_Acc1_ID=5 AND Fix_Acc2Type_ID=2 AND (Acc2RowID=2 OR Acc2RowID=3 OR Acc2RowID=4)
    ORDER BY RowID DESC;
    ''')

    # Get price and document id from mssql
    for row in ms_cur.fetch():
        global price_to_send, doch_id, acc_number
        price_to_send = (int(row['BedPrice']) * int(os.getenv('PRICE_FACTOR')))
        doch_id = row['DocH_ID']
        acc_number = row['Acc2RowID']
        break

    ms_cur.close()

    # Sadad transAction
    if (str(os.getenv('SADAD_RUN')) == 'YES') and acc_number == int(os.getenv('SADAD_ACC_ID')) and price_to_send != 0:
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
    # Pec transAction
    elif (str(os.getenv('PEC_RUN')) == 'YES') and acc_number == int(os.getenv('PEC_ACC_ID')) and price_to_send != 0:
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

            # Response file
            response_file = os.path.join(
                pec_service_api_dir+'response/', 'TransAction.txt'
            )

            # Clean old result (if exist)
            if os.path.exists(response_file):
                not_remove = True
                while not_remove:
                    try:
                        os.remove(response_file)
                        not_remove = False
                    except:
                        pass

            # Write new TransAction request for send to pay-terminal
            def write_request():
                if os.path.exists(request_file):
                    not_remove = True
                    while not_remove:
                        try:
                            os.remove(request_file)
                            not_remove = False
                        except:
                            pass

                file = open(request_file, 'w')
                file.write(
                    'Amount={}\ntype={}\nIP={}\nport={}'.format(
                        price_to_send, os.getenv('PEC_CON_TYPE'), os.getenv(
                            'PEC_DEVICE_IP'), os.getenv('PEC_DEVICE_PORT')
                    )
                )
                file.close()

            # TransAction is Sent?
            def check_for_sent():
                not_sent = True
                while(not_sent):
                    if(os.path.exists(request_file)):
                        pass
                    else:
                        not_sent = False
                        global stat
                        stat = 'درخواست ارسال شد'

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
                try:
                    os.remove(response_file)
                except:
                    pass
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
                    if r == '00':
                        return 'تراکنش موفق'
                    elif r == '99':
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

                # Get responseCode
                etxt = txt.split()
                result = '01'
                try:
                    result = etxt[2]
                except:
                    pass

                # Create Json Result
                global pec_json
                json_text = '{ "PcPosStatusCode":"'+result+'", "PcPosStatus":"' + \
                    stat+'", "ResponseCodeMessage":"' + \
                    error_message(result)+'"}'
                pec_json = jsn.loads(json_text)
                
                # For delete extra Result File
                def remove_result():
                    not_remove = True
                    while not_remove:
                        try:
                            os.remove(response_file)
                            not_remove = False
                        except:
                            pass

                # Success TransAction
                if result == '00':
                    remove_result()
                    break
                # Fail TransAction -> Show Error
                else:
                    # Gui
                    pec_gui = tk_gui()
                    pec_gui.show_message(do_trans_action, abort_pay, pec_json, 'تاپ')
                    if not_cancel == False:
                        remove_result()

            # Show result in terminal
            print('*********[Pec]*********')
            for key in pec_json:
                value = pec_json[key]
                print(key, ' : ', value)
            print('*******[End-Pec]*******')

            # Save result in sqlite pay table
            sqlite.execute('''
            INSERT INTO pay(
                id, price, status
            )VALUES(
                {}, {}, {}
            )
            '''.format(doch_id, price_to_send, pec_json['PcPosStatusCode']))
            sqlite.commit()

            # Close sqlite connection
            sqlite.close()
    # Asan-P transAction
    elif (str(os.getenv('ASAN-P_RUN')) == 'YES') and acc_number == int(os.getenv('ASAN-P_ACC_ID')) and price_to_send != 0:
        pcpos = PCPos(int(os.getenv('ASAN-P_DEVICE_PORT')))
        pcpos.InitLAN(os.getenv('ASAN-P_DEVICE_IP'))

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
            def do_trans_action():
                # price, empty, doc_id, time
                send_request = pcpos.DoSyncPayment(str(price_to_send), "", str(doch_id), DateTime.Now)
                response = str(send_request)
                end_result = re.split('= |;', response)
                return end_result

            # For cancell TransAction 
            not_done = True

            def abort_pay():
                global not_done
                not_done = False

            result = do_trans_action()
            while not_done:
                print(result)
                if result[1] == '110':
                    print(result[0]+': '+result[1])
                    print(result[3])
                    not_done = False
                else:
                    # Create Json Result
                    json_text = '{ "PcPosStatusCode":"'+result[1]+'", "PcPosStatus":"' + \
                    'فعال'+'", "ResponseCodeMessage":"' + \
                    result[3]+'"}'
                    AsanP_json = jsn.loads(json_text)
                    
                    # Show Message
                    AsanP_gui = tk_gui()
                    AsanP_gui.show_message(do_trans_action, abort_pay, AsanP_json, 'آپ')
            
            # Save result in sqlite pay table
            sqlite.execute('''
            INSERT INTO pay(
                id, price, status
            )VALUES(
                {}, {}, {}
            )
            '''.format(doch_id, price_to_send, AsanP_json['PcPosStatusCode']))
            sqlite.commit()

            # Close sqlite connection
            sqlite.close()