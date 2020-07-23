#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append('/home/shahab/dev/newshub')
sys.path.append('/home/oem/dev/newshub')
sys.path.append('/root/dev/newshub')
import elasticsearch
import requests
from bs4 import BeautifulSoup
from publics import db, es, PrintException
from datetime import datetime
from bson import ObjectId
from queue import Queue, Empty
import threading
import urllib3
import time
import subprocess
# import sub

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

col_news = db()['news']
col_engine_instances = db()['engine_instances']
col_error_logs = db()['error_logs']
col_source_links = db()['source_links']
q = Queue()
thread_count = 25
count = 0
running = threading.Event()
news_count = 0
done = True


def kill_file():
    result = subprocess.getstatusoutput(f'ps -ef | grep python3')

    # file_names = ['text_reader.py', 'link_grabber.py']

    for item in result[1].split('\n'):
        finally_result = item.split()
        # for name in file_names:
        if 'text_reader.py' in finally_result[-1]:
            subprocess.run(['kill', '-9', finally_result[1]])


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
    for a in html.find_all('a'):
        del a['href']
    return html


def do_work(item):
        global count
        count += 1
        print(count)
        news_html = None
        item['mongo_id'] = str(item['_id'])
        del item['_id']
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        try:
            result = requests.get(item['url'], headers=headers, verify=False)
        except:
            try:
                result = requests.get(item['url'], verify=False)
            except:
                print(item['url'])
                result = ''
                log(type='get_url', page_url=item['url'], selector='', data={},
                    error=PrintException(), engine_instance_id=engine_instance_id, source_id=item['source_id'])

        status = ''
        if (result != '') or (result is not None):
            try:
                html = BeautifulSoup(result.text, 'html.parser')
            except Exception as e:
                print('--------------')
                html = ''
                print(e)
                ddd = [result, '']
                print(type(result))
                print(ddd)
            try:
                news_html = html.select(item['text_selector'])
                if len(news_html) > 0:
                    news_html = news_html[0]
                    try:
                        news_html = remove_hrefs(news_html)
                    except:
                        pass
                    status = 'text'
                    source_link_info = col_source_links.find_one({'_id': ObjectId(item['source_link_id'])})
                    if 'exclude' in source_link_info:
                        for exclude in source_link_info['exclude']:
                            for ex in news_html.select(exclude):
                                ex.decompose()
                else:
                    status = 'Empty'
                    log(type='read_text', page_url=item['url'], selector=item['text_selector'], data={},
                        error='Empty', engine_instance_id=engine_instance_id, source_id=item['source_id'])
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
                }})
        if news_html is not None and news_html != '' and len(news_html) > 0:
            try:
                news_text = news_html.text
            except:
                news_text = ''
                status = 'error_text'
                log(type='read_text', page_url=item['url'], selector=item['text_selector'], data={},
                    error=PrintException(), engine_instance_id=engine_instance_id, source_id=item['source_id'])
            item['status'] = status
            item['text'] = news_text
            item['html'] = str(news_html)
            item['text_reader_id'] = engine_instance_id
            try:
                es().index(index='newshub', doc_type='news', body=item)
            except elasticsearch.ElasticsearchException as e:
                subprocess.run(['systemctl','restart','elasticsearch'])
                es().index(index='newshub', doc_type='news', body=item)
            col_news.update_one({'_id': ObjectId(item['mongo_id'])}, {'$set': {
                'status': status,
                'text': news_text,
                'html': str(news_html),
            }})


def worker():
    global done
    while done:
        time.sleep(1)
        item = q.get()
        do_work(item)
        q.task_done()
        global count
        global news_count
        if count == news_count:
            done = False
            exit()


def run():
    for i in range(thread_count):
        t = threading.Thread(target=worker)
        t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
        t.start()
        t.killed = True
    if news_id == '':
        news_list = col_news.find({'status': 'summary'}).sort('create_date', -1)
    else:
        news_list = col_news.find({'_id': ObjectId(news_id)})
    global news_count
    q.empty()
    for item in news_list:
        news_count += 1
        item['title'] = item['title'].decode('utf-8')
        item['summary'] = item['summary'].decode('utf-8')
        item['url'] = item['url'].decode('utf-8')
        q.put(item)
    running.set()
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
news_id = ''
if len(sys.argv) > 1:
    news_id = sys.argv[1]
# kill_file()
run()
duration = (datetime.now() - start).total_seconds()

print('duration is : ', duration)
print(col_engine_instances.update_one({'_id': ObjectId(engine_instance_id)}, {'$set': {
    'duration': duration,
    'errors': error_count,
    'source_links': count,
    'new_contents': ''
}}).raw_result)
