import os, clr, re
import json as jsn
from db.db_con import SqliteDb
from gui_for_message import tk_gui
from dotenv import load_dotenv

load_dotenv()

# Load asanpardakht dll
clr.AddReference("module/PosInterface")
from PosInterface import PCPos
from System import DateTime

def asanp(doch_id, price_to_send):
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
            send_request = pcpos.DoSyncPayment(
                str(price_to_send), "", str(doch_id), DateTime.Now)
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
            print(result[1])
            if result[1] == '0':
                print(result[0]+': '+result[1])
                print(result[3])
                abort_pay()
            else:
                # Create Json Result
                json_text = '{ "PcPosStatusCode":"'+result[1]+'", "PcPosStatus":"' + \
                    'فعال'+'", "ResponseCodeMessage":"' + \
                    result[3]+'"}'
                AsanP_json = jsn.loads(json_text)

                # Show Message
                AsanP_gui = tk_gui()
                AsanP_gui.show_message(
                    do_trans_action, abort_pay, AsanP_json, 'آپ')

        # Save result in sqlite pay table
        sqlite.execute('''
            INSERT INTO pay(
                id, price, status
            )VALUES(
                {}, {}, {}
            )
            '''.format(doch_id, price_to_send, result[1]))
        sqlite.commit()

        # Close sqlite connection
        sqlite.close()
