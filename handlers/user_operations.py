# from builtins import print
from datetime import datetime
from encodings.punycode import selective_find

from bson.objectid import ObjectId
from base_handler import BaseHandler
from communications import send_sms
from publics import db
from publics import random_digits, create_md5, encode_token
from sms import sms


class Register(BaseHandler):
    def init_method(self):
        self.tokenless = True
        self.required = {
            'post': ['mobile', 'password']
        }
        self.inputs = {
            'post': ['mobile', 'password', 'email', 'referer', 'name', 'family',
                       'gender', 'ref_code', 'b_date', 'role', 'email', 'telegram', 'instagram', 'linkedin',
                       'bio', 'cover', 'pic', 'device_info', 'market']
        }

    def before_post(self):
        try:
            self.method = 'users'
            col_users = self.db['users']
            if col_users.count({'mobile': self.params['mobile']}) > 0:
                self.set_output('field_error', 'mobile_exists')
                return False
            self.params['referer'] = self.params.get('referer').upper() if self.params.get('referer') is not None else ''
            referer = self.params.get('referer').upper() if self.params.get('referer') is not None else ''
            if referer != '':
                if col_users.count({'ref_code': referer.upper()}) == 0:  # invalid ref_code:
                    self.set_output('user', 'invalid_ref_code')
                    return False
                # TODO do something for web registration

                if col_users.count({'device_info.mac_address': self.params['device_info']['mac_address']}) > 0:
                    self.set_output('user', 'multiple_registration')
                    return False
            # self.params['activation_code'] = '1'
            self.params['activation_code'] = random_digits()
            self.params['premium_date'] = ''
            # self.params['confirmed'] = True
            self.params['confirmed'] = False
            self.params['b_date'] = ''
            self.params['notification_settings'] = []
            self.params['role'] = 'user'
            self.params['password_pure'] = self.params['password']
            self.params['password'] = create_md5(self.params['password'])
        except:
            self.PrintException()
            return False
        return True

    def after_post(self):
        try:
            send_sms(sms['users']['registration_successful']['fa'] % self.params['activation_code'], self.params['mobile'])
            # send_sms(sms['users']['registration_successful'][self.locale] % self.params['activation_code'], self.params['mobile'])
                # send_registration_email(self.params['email'], self.params['activation_code'])
        except:
            self.PrintException()
        return True

    def post(self, *args, **kwargs):
        try:
            self.method = 'post'
            if self.pre_post():
                self.params.update(self.added_data)
                col = db()['users']
                self.params['create_date'] = datetime.now()
                self.params['last_update'] = datetime.now()
                id = str(col.insert(self.params))
                self.id = id
                self.output['data']['item']['id'] = id
                self.output['token'] = encode_token({'user_id': self.id}).decode('utf-8')
                self.set_output('public_operations', 'successful')
                self.after_post()
        except:
            self.PrintException()
            self.set_output('public_operations', 'failed')
        self.kmwrite()


class Login(BaseHandler):
    def init_method(self):
        self.tokenless = True
        self.required = {
            'post': ['mobile', 'password']
        }
        self.inputs = {
            'post': ['mobile', 'code', 'password', 'market'],
            # 'put': ['mobile', 'code', 'password']
        }

    def check_update(self):
        col_versions = db()['versions']
        versions = col_versions.find({'version': {'$gt': self.params['app_version']}})
        update_status = 'uptodate'
        if versions.count() > 0:
            update_status = 'optional'
        for version in versions:
            if version['type'] == 'forced':
                update_status = 'forced'
                break
        return update_status

    def before_post(self):
        try:
            print('self.params')
            print(self.params)
            col_users = db()['users']
            # col_user_logins = self.db['user_logins']
            if self.params.get('app_version') is None:
                self.params['app_version'] = self.params['version'] if 'version' in self.params else '1.0.0'
            user_info = col_users.find_one(
                {'mobile': self.params['mobile'],
                 'password': create_md5(self.params['password'])})
            # print({'mobile': self.params['mobile'],
            #      'password': create_md5(self.params['password'])})
            # print(col_users.name)
            # print(col_users.db.name)
            # print(user_info)
            if user_info is None:
                self.set_output('user', 'wrong_login_info')
            else:
                self.user_role = user_info['role']
                user_info = self.after_get_one(user_info)
                if user_info['confirmed']:
                    # print(user_info['premium_date'])
                    # print(int(user_info['premium_date'] > datetime.now()))
                    self.user_id = user_info['id']
                    self.set_output('public_operations', 'successful')
                    # premium_date = user_info.get('premium_date')
                    premium = False
                    try:
                        # print('111111111111222222222222222222')
                        # print(user_info)
                        if user_info['premium_date'] > datetime.now():
                            premium = True
                    except:
                        self.PrintException()
                    self.output['token'] = encode_token({
                        'user_id': user_info['id'],
                        'app_version': self.params['app_version'],
                        'premium': premium,
                    }).decode('utf-8')
                    # print(self.output['token'])
                    # TODO: Here update should be checked
                    user_info['update_status'] = self.check_update()
                    user_info['update_link'] = 'http://onmiz.com/#download'
                    self.user_id = user_info['id']
                    # TODO: this should be in permission system
                    if 'last_update' in user_info: del user_info['last_update']
                    if 'password_pure' in user_info: del user_info['password_pure']
                    if 'password' in user_info: del user_info['password']
                    user_info['premium_date'] = str(user_info.get('premium_date'))
                    self.output['data']['item'] = user_info
                else:
                    self.set_output('user', 'inactive')
        except:
            self.PrintException()
            self.set_output('public_operations', 'failed')
        try:
            col_user_logins = self.db['user_logins']
            col_user_logins.insert({
                'user_id': self.user_id,
                'code': self.params.get('code'),
                'mobile': self.params.get('mobile'),
                'password': self.params.get('password'),
                'imei': self.params.get('imei'),
                'app_version': self.params.get('app_version'),
                'os': self.params.get('os'),
                'status': self.status,
                'date': datetime.now(),
                'notes': self.note_id,
                'market': self.params.get('market'),
            })
        except:
            self.PrintException()
        self.allow_action = False


class Profile(BaseHandler):
    def init_method(self):
        self.casting['dates'] = ['b_date', 'premium_date']
        self.inputs = {
            'put': ['b_date', 'gender', 'name', 'family', 'email', 'pic', 'password', 'theme'],
            'get': ['all']
        }

    def put_validation_check(self):
        return True

    def before_get(self):
            try:
                fields_dic = {}
                for item in self.fields:
                    fields_dic[item] = 1
                col_users = self.db['users']
                if 'all' in self.params:
                    # print(1)
                    user_info = col_users.find_one({'_id': ObjectId(self.user_id)})
                    if 'b_date' in user_info:
                        user_info['b_date'] = str(user_info['b_date'])
                else:
                    # print(2)
                    user_info = col_users.find_one({'_id': ObjectId(self.user_id)}, fields_dic)
                user_info['id'] = str(user_info['_id'])
                user_info['premium_date'] = str(user_info['premium_date'])
                # print(user_info)
                if 'password_pure' in user_info: del user_info['password_pure']
                if 'password' in user_info: del user_info['password']
                del user_info['_id']
                self.output['data']['item'] = user_info
                del self.output['data']['item']['create_date']
                del self.output['data']['item']['last_update']
                self.set_output('public_operations', 'successful')
            except:
                self.PrintException()
                return False
            self.allow_action = False
            return True

    def put(self, *args, **kwargs):
        try:
            self.method = 'put'
            self.module = self.request.uri.split('/')[1].split('?')[0]
            if self.pre_put():
                if 'b_date' in self.params:
                    if self.params['b_date'] != '':
                        self.params['b_date'] = datetime.strptime(self.params.get('b_date'), '%Y/%m/%d')
                if 'password' in self.params:
                    # print('1111111111111111111111111111111111111111111')
                    # print(self.params)
                    self.params['password_pure'] = self.params['password']
                    self.params['password'] = create_md5(self.params['password'])
                if 'premium_date' in self.params:
                    del self.params['premium_date']
                col = db()['users']
                if 'email' in self.params:
                    self.params['email'] = self.params['email'].lower()
                    if self.params['email'] != '' and col.count({'email': self.params['email'], '_id': {'$ne': ObjectId(self.user_id)}}) > 0:
                        self.set_output('user', 'email_exists')
                        self.allow_action = False
                if self.allow_action:
                    self.params['last_update'] = datetime.now()
                    # self.Print(self.params, Colors.BLUE)
                    # print('FUCKING PARAMS')
                    # print(self.params)
                    results = col.update_one({'_id': ObjectId(self.user_id)}, {'$set': self.params}).raw_result
                    if results['nModified'] > 0:
                        self.set_output('public_operations', 'successful')
                    elif results['updatedExisting']:
                        self.set_output('public_operations', 'update_failed')
                    else:
                        self.set_output('public_operations', 'record_not_found')
                    results = col.update({'_id': ObjectId(self.user_id)}, {'$set': self.params})
        except:
            self.PrintException()
            self.set_output('public_operations', 'failed')
        self.after_put()
        self.kmwrite()


class ForgotPassword(BaseHandler):
    def init_method(self):
        print(111)
        self.tokenless = True

    def before_post(self):
        try:
            col = self.db['users']
            activation_code = random_digits()
            # activation_code = '1'
            print(self.params)
            if 'mobile' in self.params:
                user_info = col.find_one({'mobile': self.params['mobile']})
                print(user_info)
                if user_info is None:
                    self.set_output('user', 'user_not_exists')
                    return False
                results = col.update_one({'mobile': self.params['mobile']},
                                         {'$set': {'activation_code': activation_code}})
                send_sms(sms['users']['forgot_password']['fa'] % activation_code, self.params['mobile'])
                # send_sms(sms['users']['forgot_password'][self.locale] % activation_code, self.params['mobile'])
                self.set_output('public_operations', 'successful')
            # else:
            #     user_info = col.find_one({'mobile': self.params['mobile']})
            #     print('user_info')
            #     print(user_info)
            #     if user_info is None:
            #         self.set_output('user', 'user_not_exists')
            #     else:
            # else:
            # self.set_output('public_operations', 'successful')
        except:
            self.PrintException()
            self.set_output('public_operations', 'failed')
            return False
        self.allow_action = False
        return True


class ResetPassword(BaseHandler):
    def init_method(self):
        self.tokenless = True
        self.required = {
            'post': ['mobile', 'activation_code', 'new_password']
        }
        self.inputs = {
            'post': ['mobile', 'activation_code', 'new_password'],
            'put': ['mobile', 'activation_code', 'new_password']
        }
        # col_users = self.db['users']

    def before_post(self):
        try:
            print(self.params)
            col_users = self.db['users']
            results = col_users.find_one_and_update({
                'mobile': self.params['mobile'],
                'activation_code': self.params['activation_code']
            },
             {
                 '$set': {'password': create_md5(self.params['new_password']),
                 'password_pure': self.params['new_password']
              }})
            if results is None:
                self.set_output('user', 'password_reset_failed')
            else:
                self.set_output('public_operations', 'successful')
        except:
            self.PrintException()
            self.set_output('public_operations', 'failed')
            return False
        self.allow_action = False
        return True


class ResendVerificationCode(BaseHandler):
    def init_method(self):
        self.tokenless = True
        self.required = {
            'post': ['mobile']
        }
        self.inputs = {
            'post': ['mobile', 'service_id', 'request_id'],
            'put': ['mobile', 'service_id', 'request_id']
        }

    def before_post(self):
        try:
            col_users = db()['users']
            results = col_users.find_one({'mobile': self.params['mobile']})
            if results is None:
                self.set_output('user', 'mobile_not_exists')
            else:
                send_sms(sms['users']['resend_activation_code']['fa'] % results['activation_code'].encode('utf-8'), self.params['mobile'])
                # send_sms(sms['users']['resend_activation_code'][self.locale] % results['activation_code'].encode('utf-8'), self.params['mobile'])
                self.set_output('user', 'password_token_resent')

            self.allow_action = False
            return True
        except:
            self.PrintException()
            return False
