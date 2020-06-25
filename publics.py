import sys
sys.path.append('/root/dev/newshub')
db_name = 'newshub'


def PrintException():
    import linecache
    import sys
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)


def PE():
    import sys
    import traceback
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    print(''.join('!! ' + line for line in lines))  # Log it or whatever here


def es():
    from elasticsearch import Elasticsearch
    # return Elasticsearch('htps://5.63.9.73')
    return Elasticsearch('htp://localhost')


def set_db(name):
    global db_name
    db_name = name


def set_test_mode(mode):
    consts.TEST_MODE = mode


# def es():
#     from elasticsearch import Elasticsearch
#     return Elasticsearch('localhost')


def db():
    from pymongo import MongoClient
    con = MongoClient()
    return con[db_name]


def load_messages():
    messages = {}
    try:
        set_db(db_name)
        col_server_messages = db()['server_messages']
        for item in col_server_messages.find():
            group = item['group']
            name = item['name']
            if group not in messages: messages[group] = {}
            del item['group']
            del item['name']
            messages[group][name] = item
    except:
        PrintException()
    return messages


def load_notifications():
    notifications = {}
    try:
        set_db(db_name)
        col_server_notifications = db()['server_notifications']
        for item in col_server_notifications.find():
            group = item['group']
            name = item['name']
            if group not in notifications: notifications[group] = {}
            del item['_id']
            del item['group']
            del item['name']
            notifications[group][name] = item
    except:
        PrintException()
    return notifications


class consts:
    import os
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    page_size = 20
    MAX_TOKEN_DURATION = 1000000
    MESSAGES = load_messages()
    NOTIFICATIONS = load_notifications()
    CONSOLE_LOG = True
    LOG_ACTIVE = True
    PDP_ROOT = '/var/www/html/newshub/'
    PDP_IMAGES = PDP_ROOT + 'images/'
    # SERVER_ADDRESS = 'http://test.onmiz.org'
    # SERVER_ADDRESS = 'http://192.168.1.20'
    MESSAGE_SERVER_ADDRESS = 'http://logs.onmiz.org'
    SERVER_ADDRESS = 'https://news.onmiz.org'
    # SERVER_ADDRESS = 'http://192.168.1.16'
    MESSAGE_SERVER_PORT = '7070'
    SERVER_PORT = '8000'
    DB_NAME = 'newshub'
    TEST_DB_NAME = 'tnewshub'
    ODP_ROOT = SERVER_ADDRESS + '/newshub/'
    LOG_SERVER = 'http://logs.onmiz.org:8080'
    ODP_IMAGES = ODP_ROOT + 'images/'
    TEST_MODE = False
    MAIL_SERVER_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRlIjoiMjAxOC0xMC0yNyAxMjoyNDoxNC40MzMyOTEiLCJyb2xlIjoiYWRtaW4iLCJ1c2VyX2lkIjoiNWFjMzNiMGFjZjFlOGMyMzE2OTUwYzljIn0.yd5t5yaWYHV28y80QdHnU1QEjsqheRoVqObXehHpiQQ'
    MAIL_SERVER_IP = 'http://server1.onmiz.org:8585/'


def create_md5(str):
    import hashlib
    ps = hashlib.md5()
    ps.update(str.encode('utf-8'))
    _hash = ps.hexdigest()
    ps = hashlib.sha1()
    ps.update(str.encode('utf-8'))
    _hash += ps.hexdigest()[:18:-1]
    _hash = _hash[::-1]
    ps = hashlib.new('ripemd160')
    ps.update(_hash.encode('utf-8'))
    return ps.hexdigest()[3:40]


def encode_token(data):
    import jwt
    import datetime
    data['date'] = str(datetime.datetime.now())
    return jwt.encode(data, 'ThisIsASecret@2019', algorithm='HS256')


def decode_token(token):
    import jwt
    try:
        result = jwt.decode(token, 'ThisIsASecret@2019', algorithms=['HS256'])
    except:
        result = None
        PrintException()
    return result


def random_str(length):
    import random, string
    return ''.join(random.choice(string.lowercase) for i in range(length))


def random_digits():
    from random import randint
    return str(randint(1000, 9999))


def log_status(l):
    from datetime import datetime
    col = db()['logs']
    del l['date']
    l['date'] = datetime.now()
    col.insert(l)


def prepare_item(item):

    if '_id' in item:
        item['id'] = str(item['_id'])
        del item['_id']
        for k, v in item.iteritems():
            if 'date' in k:
                item[k] = str(v)
    return item


def send_email_simple(to, title, body):
    import requests
    results = requests.post(url=consts.MAIL_SERVER_IP + 'mails', json={
        'token': consts.MAIL_SERVER_TOKEN,
        'to': to,
        'title': title,
        # 'title': title,
        'body': body,
        'sent': False
    })


def send_password_reset_email(to, activation_code):
    try:
        f = open(consts.ROOT_DIR + '/templates/registration_email.html')
        email_content = f.read()
        email_content = email_content.replace('%activation_code%', activation_code)
        f.close()
        send_email_simple(to, "Password reset code for Miz", email_content)
    except:
        PrintException()


def send_registration_email(to, activation_code):
    try:
        f = open(consts.ROOT_DIR + '/templates/registration_email.html')
        email_content = f.read()
        email_content = email_content.replace('%activation_code%', activation_code)
        f.close()
        send_email_simple(to, "Activate your Miz account", email_content)
    except:
        PrintException()

