from publics import consts, db, PrintException
from bson import ObjectId
import requests
from datetime import datetime


def send_notification(action, user_id, id, title, text, user={}, data={}, date=datetime.now()):
    try:
        if not consts.TEST_MODE:
            col_sessions = db()['sessions']
            results = col_sessions.find({'user_id': user_id})
            notif_ids = []
            for item in results:
                if item['notif_id'] is not None:
                    notif_ids.append(item['notif_id'])
            if notif_ids != []:
                param_data = {
                    'action': action,
                    'user_id': str(user_id),
                    'id': str(id),
                    'title': title,
                    'text': text,
                    'user': user,
                    'data': data,
                    'date': str(date),
                    'api_key': "AAAAtpM_L08:APA91bErqD45B6pMQcYzjN9MGYMCJhW9zAM8400GXVqGWu5l-TrRqGxBj-LPog6Cal1uxBpg3IOeCK5wrvof2ghoF2JA2A7etCbkr_x_OIYUMJkftFSbri9YppyzRa2PD6pgv7RoKg4C",
                    'notif_ids': notif_ids,
                }
                print(param_data)
                result = requests.post(url='%s:%s/v1/notifications' % (consts.MESSAGE_SERVER_ADDRESS, consts.MESSAGE_SERVER_PORT),
                                    json=param_data).json()

                print('result')
                print(result)
    except:
        PrintException()


def send_sms(text, number, date=datetime.now()):
    try:
        print('text')
        print(text)
        print(number)
        param_data = {
            'mobile': number,
            'text': text,
            'date': str(date)
        }
        print('%s:%s/v1/sms' % (consts.MESSAGE_SERVER_ADDRESS, consts.MESSAGE_SERVER_PORT))
        print(param_data)
        if not consts.TEST_MODE:
            result = requests.post(url='%s:%s/v1/sms' % (consts.MESSAGE_SERVER_ADDRESS, consts.MESSAGE_SERVER_PORT), json=param_data)
        print(result.text)
        # print(result.json())
        print(result.status_code)
    except:
        print('KOOOOOOOOOOOOOOOON')
        PrintException()
