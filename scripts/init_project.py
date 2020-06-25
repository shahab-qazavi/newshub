import sys
sys.path.append('/root/dev/newshub')
from publics import db, create_md5, set_db
set_db('newshub')


def insert_users():
    col_users = db()['users']
    if col_users.count_documents({'mobile': 'admin'}) == 0:
        col_users.insert_one({
            'name': 'ehsan',
            'family': 'shirzadi',
            'mobile': 'admin',
            'password': create_md5('1'),
            'role': 'admin',
            'confirmed': True,
        })


def insert_messages():
    print(db().name)
    col_server_messages = db()['server_messages']
    col_server_messages.drop()
    col_server_messages.insert_many([
        {
            'group': 'user',
            'name': 'token_not_received',
            'code': 401,
            'status': False,
            'en': 'Token not received'
        },
        {
            'group': 'user',
            'name': 'token_validated',
            'code': 200,
            'status': True,
            'en': 'Token validated'
        },
        {
            'group': 'user',
            'name': 'inactive',
            'code': 401,
            'status': False,
            'en': 'User is inactive'
        },
        {
            'group': 'user',
            'name': 'password_token_resent',
            'code': 200,
            'status': True,
            'en': 'Token has been sent'
        },
        {
            'group': 'user',
            'name': 'user_not_exists',
            'code': 401,
            'status': False,
            'en': 'User not exists'
        },
        {
            'group': 'user',
            'name': 'token_expired',
            'code': 401,
            'status': False,
            'en': ''
        },
        {
            'group': 'user',
            'name': 'access_denied',
            'code': 401,
            'status': False,
            'en': 'Access denied'
        },
        {
            'group': 'user',
            'name': 'premium_account_required',
            'code': 402,
            'status': False,
            'en': 'Premium account required'
        },
        {
            'group': 'user',
            'name': 'permission_not_defined',
            'code': 401,
            'status': False,
            'en': 'Permission not defined'
        },
        {
            'group': 'user',
            'name': 'method_not_specified',
            'code': 401,
            'status': False,
            'en': 'Method not specified'
        },
        {
            'group': 'user',
            'name': 'wrong_login_info',
            'code': 400,
            'status': False,
            'en': 'Wrong login info'
        },
        {
            'group': 'user',
            'name': 'access_granted',
            'code': 200,
            'status': True,
            'en': 'Access granted'
        },
        {
            'group': 'public_operations',
            'name': 'params_loaded',
            'code': 200,
            'status': True,
            'en': 'Params loaded'
        },
        {
            'group': 'public_operations',
            'name': 'params_not_loaded',
            'code': 401,
            'status': False,
            'en': 'Params not loaded'
        },
        {
            'group': 'public_operations',
            'name': 'page_limit',
            'code': 401,
            'status': False,
            'en': 'Page limit reached'
        },
        {
            'group': 'public_operations',
            'name': 'record_not_found',
            'code': 401,
            'status': False,
            'en': 'Record not found'
        },
        {
            'group': 'public_operations',
            'name': 'failed',
            'code': 401,
            'status': False,
            'en': 'Operation failed'
        },
        {
            'group': 'public_operations',
            'name': 'successful',
            'code': 200,
            'status': True,
            'en': 'Operation successful'
        },
        {
            'group': 'field_error',
            'name': 'required',
            'code': 401,
            'status': False,
            'en': 'Field %s required'
        },
        {
            'group': 'field_error',
            'name': 'mobile_exists',
            'code': 400,
            'status': False,
            'en': 'Mobile exists'
        },
        {
            'group': 'field_error',
            'name': 'null',
            'code': 401,
            'status': False,
            'en': 'Null not allowed'
        },
        {
            'group': 'field_error',
            'name': 'id_format',
            'code': 401,
            'status': False,
            'en': 'ID format is not correct'
        },
        {
            'group': 'user',
            'name': 'login_failed',
            'code': 401,
            'status': False,
            'en': 'Login information is not correct'
        },
        {
            'group': 'user',
            'name': 'logged_in',
            'code': 401,
            'status': False,
            'en': 'Logged in'
        },
        {
            'group': 'crawler',
            'name': 'selector_undefined',
            'code': 401,
            'status': False,
            'en': 'Selector undefined: %s'
        }
    ])

insert_users()
insert_messages()
