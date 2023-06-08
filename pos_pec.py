import os
from gui_for_message import tk_gui
from db.db_con import SqliteDb
import json as jsn

def pec(doch_id, price_to_send, gui_tray):
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
            while (not_sent):
                if (os.path.exists(request_file)):
                    pass
                else:
                    not_sent = False
                    global stat
                    stat = 'درخواست ارسال شد'

        # Check for receive response
        def check_for_receive():
            response_is_not_exits = True
            while (response_is_not_exits):
                if (os.path.exists(response_file)):
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
        while (not_cancel):
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
                pec_gui.show_message(
                    do_trans_action, abort_pay, pec_json, 'تاپ')
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