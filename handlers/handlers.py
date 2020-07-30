from publics import encode_token
from base_handler import BaseHandler
import requests
from bs4 import BeautifulSoup
from bson import ObjectId
from publics import PrintException, PE, es
import datetime
from random import randint


class Source(BaseHandler):
    def init_method(self):
        self.required = {
            'post': ['url', 'name', 'logo']
        }
        self.inputs = {
            'post': ['url', 'name', 'logo', 'enabled'],
            'put': ['url', 'name', 'logo', 'enabled']
        }
        # print(self.db.name)
        self.tokenless = True

    def before_get(self):
        print('self.user_role')
        print(self.user_role)
        try:
#             if self.user_role == 'user':
            self.conditions['enabled'] = True
        except:
            self.PrintException()
            return False
        return True



class Categories(BaseHandler):
    def init_method(self):
        self.required = {
            'post': ['name']
        }
        self.inputs = {
            'post': ['name'],
            'put': ['name']
        }
        # print(self.db.name)
        self.tokenless = True


class SourceLink(BaseHandler):
    def init_method(self):
        self.required = {
            'post': ['base_url', 'url', 'box', 'link', 'summary', 'date', 'title', 'source_id']
        }
        self.inputs = {
            'post': ['base_url', 'url', 'box', 'link', 'summary', 'date', 'title', 'image', 'text', 'source_id',
                     'excludes', 'enabled'],
            'put': ['base_url', 'url', 'box', 'link', 'summary', 'date', 'title', 'image', 'text', 'source_id',
                    'excludes', 'enabled']
        }
        self.tokenless = True


class ErrorLogs(BaseHandler):
    def init_method(self):
        self.casting['dates'] = ['date']
        self.tokenless = True


class EngineInstances(BaseHandler):
    def init_method(self):
        self.casting['dates'] = ['start_date']
        self.tokenless = True


class Search(BaseHandler):
    def init_method(self):
        self.required = {

        }
        self.inputs = {

        }
        # print(self.db.name)
        self.tokenless = True

    def before_get(self):
            try:
                print('self.params')
                print(self.params)
                print('self.conditions')
                print(self.conditions)
                self.module = 'news'
            except:
                self.PrintException()
                return False
            return True


def remove_hrefs(html):
    for a in html.findAll('a'):
        del a['href']
    return html


class TestCrawl(BaseHandler):
    def init_method(self):
        # self.required = {
        #     # 'get': ['source_id']
        # }
        self.inputs = {
            'get': ['source_id', 'news_link']
        }
        self.tokenless = True

    def before_get(self):
            try:
                print(self.params)
                col_test_news = self.db['test_news']
                col_source_links = self.db['source_links']
                source_link_info = col_source_links.find_one({'_id': ObjectId(self.params['source_id'])})
                if 'news_link' in self.params:
                    print('PLAN A')
                    result = requests.get(self.params['news_link'], verify=False)
                    print(result)
                    html = BeautifulSoup(result.text, 'html.parser')
                    if 'text_selector' not in source_link_info:
                        self.set_output('crawler', 'selector_undefined', 'text_selector')
                        return False
                    news_html = html.select(source_link_info['text_selector'])[0]
                    news_html = remove_hrefs(news_html)
                    if 'exclude' in source_link_info:
                        for exclude in source_link_info['exclude']:
                            for ex in news_html.select(exclude):
                                ex.decompose()
                    news_text = news_html.text
                    self.output['data']['item'] = {
                        'text': news_text,
                        'html': news_html,
                    }
                else:
                    print('PLAN B')
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                    result = requests.get(source_link_info['url'], headers=headers, verify=False)
                    print(result)
                    html = BeautifulSoup(result.text, 'html.parser')
                    col_test_news.drop()
                    for item in html.select(source_link_info['box']):
                        if col_test_news.count({'url': source_link_info['base_url'] + item.select(source_link_info['link'])[0]['href']}) == 0:
                            try:
                                image = item.select(source_link_info['image'])[0]['src']
                            except:
                                image = ''
                            try:
                                try:
                                    date = item.select(source_link_info['date'])[0].text
                                except:
                                    date = ''
                                href = item.select(source_link_info['link'])
                                if len(href) != 0:
                                    href = href[0]['href']
                                if 'https://ana.press/' in source_link_info['url']:
                                    href = 'fa/'+item['href']
                                print(col_test_news.insert({
                                    'url': source_link_info['base_url'] + href,
                                    'title': item.select(source_link_info['title'])[0].text,
                                    'summary': item.select(source_link_info['summary'])[0].text,
                                    'date': date,
                                    'source_url': source_link_info['url'],
                                    'image': image,
                                    'status': 'summary',
                                }))
                            except Exception as e:
                                print(e)
                                PrintException()
                                PE()
                    self.output['data']['list'] = self.prepare_dataset(col_test_news.find())
                self.allow_action = False
            except:
                self.PrintException()
                return False
            return True


class MyNews(BaseHandler):
    def init_method(self):
        self.required = {
            'get': ['keywords', 'source_ids'],
        }
        self.inputs = {
            'get': ['keywords', 'source_ids', 'category_id'],
        }
        self.casting['dics'] = ['keywords', 'source_ids']

    def before_get(self):
        try:
            # print(self.premium)
            # print(self.user_id)
            if self.premium:
                if self.id is not None:
                    pass
                else:
                    keywords_query = []
                    i = 0
                    sort = [
                        {'create_date': {'order': 'desc'}}
                    ]
                    doc = {
                        "query": {
                            "bool": {
                                # "should": should_list
                            }
                        },
                        "sort": sort
                    }
                    for keyword in self.params['keywords']:
                        # if i == 2:
                        #     continue
                        # i += 1
                        # print("==========================")
                        # print(keyword)
                        # if keyword != 'دهه فجر'
                        keywords_query.append(
                            {
                                "multi_match": {
                                    "query": keyword,
                                    "fields": [
                                        "title",
                                    ],
                                    "type": "cross_fields",
                                    "operator": "AND"
                                }
                            }
                        )

                    # print(self.params['source_ids'])
                    must_query = []
                    if self.params['source_ids'] != []:
                        # get list of enabled sources
                        source_ids = []
                        for source_id in self.params['source_ids']:
                            source_ids.append({'_id': ObjectId(source_id)})
                        col_sources = self.db['sources']
                        sources = col_sources.find({
                            '_id': {'$in': source_ids},
                            'enabled': True
                        })
                        print()

                        # x = []
                        # for item in self.params['source_ids']:
                        #     x.append(item)
                        # print(doc)
                        must_query = [{"terms": {
                                            "source_id": self.params['source_ids'],
                                            "boost": 1.0
                                        }}]
                        # doc["query"]['bool']['must'] =
                    keywords_query = {
                        "bool": {"should": keywords_query}
                    }
                    # must_query = must_query + keywords_query
                    must_query.append(keywords_query)
                    doc["query"]['bool']['must'] = must_query


                        # print(doc)
                    # import json
                    # f = open('query.txt', 'wb')
                    # s = json.dumps(doc)
                    # encoded_unicode = s.encode("utf8")
                    # f.write(encoded_unicode)
                    # f.close()


                    # a_file = open("textfile.txt", "wb")
                    # a_file.write(encoded_unicode)
                    # print(self.params['page'])
                    # print(self.params['page_size'])
                    # print(self.params['page'] - 1)
                    # del doc['sort']
                    doc['from'] = (self.params['page'] - 1) * self.params['page_size']
                    doc['size'] = self.params['page_size']
                    # print("=============================")
                    import json
                    # print(json.dumps(doc))
                    # print('Going to search')
                    # print(es())
                    result = es().search(index='newshub', body=doc)
                    # print('searched!')
                    # print(result)


                    result_list = []
                    for item in result['hits']['hits']:
                        result_list.append({
                            'title': item['_source']['title'],
                            'source_id': item['_source']['source_id'],
                            'source_name': item['_source']['source_name'],
                            'mongo_id': item['_source']['mongo_id'],
                            'summary': item['_source']['summary'],
                            'image': item['_source']['image'],
                            'category_id': item['_source']['category_id'],
                            'create_date': item['_source']['create_date'],
                            'id': item['_id'],
                        })
                        # print(item['_source']['create_date'])
                        # print(item['_source']['title'])
                    self.output['data']['list'] = result_list
                    self.allow_action = False
                self.set_output('public_operations', 'successful')
            else:
                self.set_output('user', 'premium_account_required')
                return False
        except:
            self.PrintException()
            return False
        return True


class News(BaseHandler):
    def init_method(self):
        self.module = 'news'
        self.required = {
        }
        self.inputs = {
        }
        self.tokenless = True
        self.conditions
    def before_get(self):
        try:
#             if self.user_role == 'user':
            self.conditions['text'] = {'$ne':''}
        except:
            self.PrintException()
            return False
        return True
    
    def after_get_one(self, document):
        document = self.prepare_item(document)
        # if self.params.get('similars') is not None:
        # TODO Hardcode!
        col_news = self.db['news']
        result = self.prepare_dataset(col_news.find({'category_id': document['category_id'], 'text': {'$ne':''}},
                                                    {'image': 1, 'title': 1, 'summary': 1, 'create_date': 1, '_id':1}).limit(12).sort('create_date',-1))
        document['similar'] = result
        return document


class ExtLogin(BaseHandler):
    def init_method(self):
        self.module = 'users'
        self.required = {
        }
        self.inputs = {
        }
        self.tokenless = True


class PremiumPackages(BaseHandler):
    def init_method(self):
        self.required = {
            'post': ['days', 'price', 'title']
        }
        self.inputs = {
            'post': ['days', 'price', 'title']
        }
        self.casting['ints'] = ['days', 'price']
        self.tokenless = True


# class PremiumPackageOrders(BaseHandler):
#     def init_method(self):
#         self.required = {
#             'post': ['package_id', 'days', 'price', 'title']
#         }
#
#         self.inputs = {
#             'post': ['days', 'price', 'title']
#         }
#         self.casting['ints'] = ['days', 'price']
#         self.tokenless = True





    # def before_get(self):
    #         try:
    #             col_test_news = self.db['test_news']
    #             col_source_links = self.db['source_links']
    #             source_info = col_source_links.find_one({'source_id': self.params['source_id']})
    #             print(col_source_links.count())
    #             print(source_info)
    #             result = requests.get(source_info['url'], verify=False)
    #             html = BeautifulSoup(result.text, 'html.parser')
    #             col_test_news.drop()
    #             for item in html.select(source_info['box']):
    #                 if col_test_news.count({'url': source_info['base_url'] + item.select(source_info['link'])[0]['href']}) == 0:
    #                     col_test_news.insert({
    #                         'url': source_info['base_url'] + item.select(source_info['link'])[0]['href'],
    #                         'title': item.select(source_info['title'])[0].text,
    #                         'summary': item.select(source_info['summary'])[0].text,
    #                         'date': item.select(source_info['date'])[0].text,
    #                         'source_url': source_info['url'],
    #                         'image': item.select(source_info['image'])[0]['src'],
    #                         'status': 'summary',
    #                     })
    #             self.output['data']['list'] = self.prepare_dataset(col_test_news.find())
    #             self.allow_action = False
    #         except:
    #             self.PrintException()
    #             return False
    #         return True
    #



class Run(BaseHandler):
    def init_method(self):
        self.inputs = {
            'get': ['type']
        }
        self.tokenless = True

    def before_get(self):
            try:
                # print(self.params['type'])
                if self.params['type'] == 'link':
                    from daemons.link_grabber import run
                elif self.params['type'] == 'text':
                    from daemons.text_reader import run
                elif self.params['type'] == 'drop_mongo_news':
                    # print('Dropping mongo news...')
                    # print(self.db)
                    col_news = self.db['news']
                    col_news.drop()
                elif self.params['type'] == 'drop_elastic_news':
                    from elasticsearch import Elasticsearch
                    es = Elasticsearch()
                    es.indices.delete(index='newshub', ignore=[400, 404])
                elif self.params['type'] == 'drop_error_logs':
                    col_error_logs = self.db['error_logs']
                    col_error_logs.drop()
                elif self.params['type'] == 'drop_engine_instances':
                    col_engine_instances = self.db['engine_instances']
                    col_engine_instances.drop()
                elif self.params['type'] == 'drop_all':
                    col_error_logs = self.db['error_logs']
                    col_error_logs.drop()
                    col_engine_instances = self.db['engine_instances']
                    col_engine_instances.drop()
                    from elasticsearch import Elasticsearch
                    es = Elasticsearch()
                    es.indices.delete(index='newshub', ignore=[400, 404])
                    col_news = self.db['news']
                    col_news.drop()
                self.allow_action = False
            except:
                self.PrintException()
                return False
            return True


class Home(BaseHandler):
    def init_method(self):
        self.inputs = {
            'get': []
        }
        self.tokenless = True

    def before_get(self):
            try:
                # TODO: news must be read from elasticsearch
                col_news = self.db['news']
                if self.params.get('header') == 'header':
                    print(1)
                    # print()
                    news = self.prepare_dataset(col_news.find({'summary': {'$ne':''} , 'text': {'$ne': ''}}).limit(1).sort('create_date',-1))
                    print(news[0])
                    self.output['data']['item']['header_news'] = [{
                        'mongo_id': news[0]['id'],
                        'title': news[0]['title'],
                        'summary': news[0]['summary'],
                    }]
                else:
                    # print(1)
                    news = self.prepare_dataset(col_news.find().limit(8).sort('create_date',-1))
                    col_sources = self.db['sources']
                    sources = self.prepare_dataset(col_sources.find({'enabled': True}).limit(9))
                    self.output['data']['item'] = {
                        'sources': sources,
                        'news': news,
                    }
                self.allow_action = False
            except:
                self.PrintException()
                return False
            return True

# TODO: For test purpose
class Fuck(BaseHandler):
    def init_method(self):
        self.inputs = {
        }
        self.tokenless =True

    def before_get(self):
        try:
            print('KOS')
            col_users = self.db['users']
            if self.params.get('type') == 'shahab':
                col_users.remove({"mobile": "9191354355"})
            if self.params.get('type') == 'profile':
                user_info = col_users.find_one({"mobile": "9157367995"})
                print(user_info)
                print(user_info['premium_date'])
                print(type(user_info['premium_date']))
                print(str(type(user_info['premium_date'])))
                self.output['data'] = {
                    'premium_date': user_info['premium_date'],
                    'premium_date_type': str(type(user_info['premium_date'])),
                    'password_pure': user_info['password_pure'],
                }

            else:
                print('KOON')
                col_users.remove({"mobile": "9157367995"})
            self.allow_action = False
        except:
            self.PrintException()
            return False
        return True


# TODO: For test purpose
class ConfirmUser(BaseHandler):
    def init_method(self):
        self.inputs = {
        }
        # self.tokenless =True

    def before_post(self):
        try:
            col_users = self.db['users']
            # result = col_users.update({"mobile": self.params['mobile'],
            print('---------------------')
            print(self.user_id)
            print(self.params['activation_code'])
            print(self.params)
            print('---------------------')
            result = col_users.update({"_id": ObjectId(self.user_id),
                                  "activation_code" : self.params['activation_code']}, {'$set': {'confirmed': True}})
            if result['nModified'] == 1:
                self.output['data']['token'] = encode_token({'user_id': str(self.user_id)}).decode()
                self.set_output('public_operations', 'successful')
            else:
                self.set_output('public_operations', 'failed')
            self.allow_action = False
        except:
            self.set_output('public_operations', 'failed')
            print(self.PrintException())
            return False
        return True


class Payment(BaseHandler):
    def init_method(self):
        self.required = {
            'post': ['package_id', 'user_id'],
            'put': ['payment_token', 'result_code', 'invoice_number', 'hashed_card_no', 'reference_id', 'amount', 'cno',
                    'message', 'card_no'],
        }
        self.casting['ints'] = ['price', 'seq_id', 'amount']
        # print(1)
        self.tokenless = True

    def before_post(self):
        try:
            print(self.params)
            col_premium_packages = self.db['premium_packages']
            premium_package_info = col_premium_packages.find_one({'_id': ObjectId(self.params['package_id'])})
            self.params['price'] = premium_package_info['price']
            self.params['package_title'] = premium_package_info['title']
            # self.params['price'] = premium_package_info['price']
            if premium_package_info['price'] == 0:
                # print(8)
                # print(self.params['user_id'])
                col_users = self.db['users']
                # print(premium_package_info['title'])
                print(col_users.update_one({'_id': ObjectId(self.params['user_id'])}, {'$set': {
                    'premium_date': datetime.datetime.now() + datetime.timedelta(days=premium_package_info['days']),
                    'last_package_days': premium_package_info['days'],
                    'last_package_title': premium_package_info['title']},
                }).raw_result)
                print(9)
                self.output['token'] = encode_token({
                    'user_id': self.params['user_id'],
                    # 'app_version': self.params['app_version'],
                    'premium': True,
                }).decode('utf-8')
            else:
                col_payments = self.db['payments']
                result = col_payments.find({}).sort('seq_id', -1).limit(1)
                print('result.count()')
                print(result.count())
                seq_id = 1 if result.count() == 0 else result[0]['seq_id'] + 1
                self.params['user_id'] = self.params['user_id']
                self.params['seq_id'] = seq_id
                self.set_output('public_operations', 'successful')
                print(2)
            return True
            # else:
            #     self.set_output('public_operations', 'failed')
            #     return False
        except:
            self.PrintException()
            return False

    def after_post(self):
        try:
            if self.params['price'] != 0:
                self.output['data']['item']['seq_id'] = self.params['seq_id']
            self.output['data']['item']['price'] = self.params['price']
            # self.output['data']['item']['package_id'] = self.params['package_id']
        except:
            self.PrintException()
            return False
        return True

    def before_put(self):
        try:
            # print('JOIOOOOOOOOOOOOOOOOON')
            # print(self.params['amount'])
            col_payments = self.db['payments']
            col_users = self.db['users']
            col_premium_packages = self.db['premium_packages']
            if self.params['result_code'] == '150':
            # if self.params['result_code'] == '100':
                payments_info = col_payments.find_one({'seq_id': self.params['seq_id']})
                premium_package_info = col_premium_packages.find_one({'_id': ObjectId(payments_info['package_id'])})

                # if int(self.params['amount']) == premium_package_info['price']:
                if int(self.params['amount']) == premium_package_info['price']:
                    # print(11)
                    # date_1 = datetime.datetime.now()
                    # print(payments_info)
                    col_users.update_one({'_id': ObjectId(payments_info['user_id'])}, {'$set': {
                        'premium_date': datetime.datetime.now() + datetime.timedelta(days=premium_package_info['days'])},
                        'last_package': premium_package_info['title']})
                    # print(222)
                else:
                    self.set_output('', '')
            else:
                # print(20)
                self.set_output('public_operations', 'failed')
            self.conditions = {'seq_id': self.params['seq_id']}
            self.allow_action = False
        except Exception as e:
            # print('KOOOOOOOOOOOOOOOON')
            # print(str(e))
            PrintException()
            return False
        return True

    # def after_put(self):
    #     try:
    #
    #         # if self.params['result_code'] == '100':
    #             # from handlers.users.user_operations import get_user_wallet_amount
    #             # col_payment = self.db['payments']
    #             # payment_info = col_payment.find_one({'seq_id': self.params['seq_id']})
    #             # if payment_info is not None:
    #             #     col_wallet = self.db['wallet']
    #             #     if col_wallet.count({'seq_id': payment_info['seq_id']}) == 0:
    #             #         # TODO: Online is hard code!
    #             #         col_wallet.insert({
    #             #             "create_date": datetime.now(),
    #             #             "description": "پرداخت آنلاین",
    #             #             "title": "آنلاین",
    #             #             "coins": self.params['amount'] / 10,
    #             #             "admin_id": "",
    #             #             "user_id": payment_info['user_id'],
    #             #             "seq_id": payment_info['seq_id'],
    #             #             "last_update": datetime.now()
    #             #         })
    #             #         col_users = self.db['users']
    #             #         self.user_id = payment_info['user_id']
    #             #         col_users.update_one({'_id': ObjectId(payment_info['user_id'])},
    #             #                                    {'$set': {'wallet': get_user_wallet_amount(self)}})
    #     except:
    #         self.PrintException()
