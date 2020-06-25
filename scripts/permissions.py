import sys
sys.path.append('/root/dev/newshub')
from publics import db, set_db
set_db('newshub')

col_users_roles = db()['users_roles']
col_users_roles.drop()
col_users_roles.insert_many([
    {
        'name': 'admin',
        'module': 'users',
        'permissions': {
            'allow': ['get'],
            'get': {}
        },
    },
    {
        'name': 'user',
        'module': 'profile',
        'permissions': {
            'allow': ['get', 'put'],
            'get': {'user_id':'$uid'},
            'put': {
                'query': {'user_id':'$uid'},
                'set': {}

            },
        },
    },
    {
        'name': 'user',
        'module': 'my_news',
        'permissions': {
            'allow': ['get'],
            'get': {},
        },
    },
    {
        'name': 'user',
        'module': 'sources',
        'permissions': {
            'allow': ['get'],
            'get': {},
        },
    },
    {
        'name': 'admin',
        'module': 'sources',
        'permissions': {
            'allow': ['get', 'post', 'put', 'delete'],
            'get': {},
        },
    },
    {
        'name': 'user',
        'module': 'confirm_user',
        'permissions': {
            'allow': ['post'],
            'post': {},
        },
    },

])
