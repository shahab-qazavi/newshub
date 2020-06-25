#!/usr/bin/env python
# -*- coding: utf-8 -*-
print('KOOOOOOOOOOOOOOOOOOOOON')
import sys
sys.path.append('/home/ehsan/dev/newshub')
sys.path.append('/root/dev/newshub')
import requests
from bs4 import BeautifulSoup
from publics import db, es, PrintException
from datetime import datetime
from bson import ObjectId

col_news = db()['news']
# col_engine_logs = db()['engine_logs']
col_engine_instances = db()['engine_instances']
col_error_logs = db()['error_logs']
col_source_links = db()['source_links']
news_id = ''
if len(sys.argv) > 1:
    news_id = sys.argv[1]
print(news_id)

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from queue import Queue
import threading
q = Queue()
thread_count = 30

def log(type, page_url, selector, data, error, source_id, engine_instance_id):
    try:
        global error_count
        error_count += 1
        col_error_logs.insert_one({
            'engine_instance_id': str(engine_instance_id),
            'type': type,
            'source_id': source_id,
            'page_url': page_url,
            'selector': selector,
            'data': data,
            'date': datetime.now(),
            'error': error,
        })
    except:
        PrintException()


def remove_hrefs(html):
    for a in html.findAll('a'):
        del a['href']
    return html


def do_work(item):
    # try:
        news_html = None
        item['mongo_id'] = str(item['_id'])
        del item['_id']
        # print(item['url'])
        result = requests.get(item['url'], verify=False)
        # print(result)
        html = BeautifulSoup(result.text, 'html.parser')
        try:
            news_html = html.select(item['text_selector'])[0]
            news_html = remove_hrefs(news_html)

            status = 'text'
            source_link_info = col_source_links.find_one({'_id': ObjectId(item['source_link_id'])})
            # with open("temp.html", "w") as file:
            #     file.write(str(news_html))
            if 'exclude' in source_link_info:
                for exclude in source_link_info['exclude']:
                    for ex in news_html.select(exclude):
                        ex.decompose()
            # with open("tempdec.html", "w") as file:
            #     file.write(str(news_html))
        except Exception as e:
            news_html = ''
            status = 'error_text'
            log(type='read_text', page_url=item['url'], selector=item['text_selector'], data={},
                error=PrintException(), engine_instance_id=engine_instance_id, source_id=item['source_id'])
            col_news.update_one({'_id': ObjectId(item['mongo_id'])}, {'$set': {
                'status': 'error',
                'text': '',
                'html': '',
                'error': str(e),
                # 'error_details': {'url': item['url']},
            }})

        if news_html is not None and news_html != '':
            # print(type(news_html))
            # print(news_html)
            news_text = news_html.text
            item['status'] = status
            item['text'] = news_text
            item['html'] = str(news_html)
            item['text_reader_id'] = engine_instance_id
            es().index(index='newshub', doc_type='news', body=item)
            col_news.update_one({'_id': ObjectId(item['mongo_id'])}, {'$set': {
                'status': status,
                'text': news_text,
                'html': str(news_html),
            }})

    # except Exception as e:
    #     print('FUCKED UP')
    #     print(e)
    #     PrintException()
    #     col_news.update_one({'_id': ObjectId(item['mongo_id'])}, {'$set': {
    #         'status': 'error',
    #         'text': '',
    #         'html': news_html,
    #         'error': str(e),
    #     }})
    #
    #     log(type='read_url', page_url=item['url'], selector='', data={}, error=PrintException(),
    #         engine_instance_id=engine_instance_id, source_id=item['source_id'])


def worker():
    while True:
        item = q.get()
        do_work(item)
        q.task_done()


def run():
    if news_id == '':
        news_list = col_news.find({'status': 'summary'}).sort('create_date', -1)
        # print(news_list.count())

    else:
        news_list = col_news.find({'_id': ObjectId(news_id)})
    for i in range(thread_count):
        t = threading.Thread(target=worker)
        t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
        t.start()
    for item in news_list:
        item['title'] = item['title'].decode('utf-8')
        item['summary'] = item['summary'].decode('utf-8')
        item['url'] = item['url'].decode('utf-8')
        q.put(item)
    q.join()


start = datetime.now()
source_links = 0
engine_instance_id = str(col_engine_instances.insert_one({
    'type': 'text',
    'start_date': start,
    'duration': -1,
    'source_links': -1,
    'errors': -1,
    'new_contents': -1,
}).inserted_id)
error_count = 0
new_contents = 0
# source_id = ''
# if len(sys.argv) > 1:
#     print(sys.argv[1])
#     source_id = sys.argv[1]
run()
duration = (datetime.now() - start).total_seconds()

col_engine_instances.update_one({'_id': ObjectId(engine_instance_id)}, {'$set': {
    'duration': duration,
    'errors': error_count,
    'source_links': source_links,
    'new_contents': ''
}})
print(duration)

