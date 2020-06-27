#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('/home/oem/dev/newshub')
sys.path.append('/root/dev/newshub')
from publics import db, PrintException
from datetime import datetime
from bson import ObjectId
col_news = db()['news_test']
col_sources = db()['sources']
col_source_links = db()['source_links']
col_engine_instances = db()['engine_instances_test']
col_error_logs = db()['error_logs_test']
link_count = 0
from queue import Queue
import threading
q = Queue()
thread_count = 10
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def create_md5(string):
    import hashlib
    hash_object = hashlib.md5(string.encode())
    return hash_object.hexdigest()


def log_error(type, page_url, selector, data, error, source_id, source_link_id, engine_instance_id, module):
    try:
        global error_count
        error_count += 1
        # print('Log created')
        # print(error)
        col_error_logs.insert_one({
            'engine_instance_id': str(engine_instance_id),
            'type': type,
            'source_id': source_id,
            'source_link_id': source_link_id,
            'page_url': page_url,
            'selector': selector,
            'data': data,
            'date': datetime.now(),
            'error': error,
        })
    except:
        PrintException()
        print('LOG PRODUCED LOG!')


def get_page(url):
    import requests
    from bs4 import BeautifulSoup
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    if 'mehrnews' not in url:
        result = requests.get(url, headers=headers, verify=False)
    elif 'mehrnews' in url:
        result = requests.get(url, verify=False)
    if 'econews' in url:
        print(result)
    f = open('temp.html', 'w')
    f.write(result.text)
    f.close()
    return BeautifulSoup(result.text, 'html.parser')


def do_work(item_info):
    # print('Working')
    source_link = item_info['source_link']
    source = item_info['source']

    try:

        global link_count
        global new_contents
        link_count += 1

        html = get_page(source_link['url'])

        for item in html.select(source_link['box']):
            href = item.select(source_link['link'])
            if len(href) != 0:
                href = href[0]['href']
            if 'https://ana.press' in source_link['url']:
                href = 'fa/' + item['href']
            # href = item.select(source_link['link'])[0]['href']
            if href[:2] == '..': href = href.replace('..', '')
            # if col_news.count_documents({'url': source_link['base_url'] + item.select(source_link['link'])[0]['href']}) == 0:

            if col_news.count_documents({'url': source_link['base_url'] + href}) == 0:
                try:
                    url = source_link['base_url'] + href

                except:
                    PrintException()
                    url = ''
                    log_error(type='read_url', page_url=source_link['url'], selector='', data={},
                              error=PrintException(), source_id=str(source['_id']),
                              source_link_id=str(source_link['_id']), engine_instance_id=engine_instance_id, module='link_grabber')
                try:

                    title = item.select(source_link['title'])[0].text
                except:
                    PrintException()
                    title = ''

                    log_error(type='extract_title', page_url=source_link['url'], selector=source_link['title'], data={},
                              error=PrintException(), source_id=str(source['_id']),
                              source_link_id=str(source_link['_id']), engine_instance_id=engine_instance_id, module='link_grabber')
                try:
                    summary = item.select(source_link['summary'])[0].text
                except:
                    PrintException()
                    summary = ''
                    log_error(type='extract_summary', page_url=source_link['url'], selector=source_link['summary'],
                              data={}, error=PrintException(), source_id=str(source['_id']),
                              source_link_id=str(source_link['_id']), engine_instance_id=engine_instance_id, module='link_grabber')
                try:
                    date = item.select(source_link['date'])[0].text
                except:
                    PrintException()
                    date = ''
                    log_error(type='extract_date', page_url=source_link['url'], selector=source_link['date'], data={},
                              error=PrintException(), source_id=str(source['_id']),
                              source_link_id=str(source_link['_id']), engine_instance_id=engine_instance_id, module='link_grabber')
                try:
                    selected = item.select(source_link['image'])
                    image = selected[0]['src'] if len(selected) > 0 else ''
                    if source_link['url'] not in image:
                        if image[0] != '/': image = '/'+image
                        image = source_link['url']+image


                except:
                    PrintException()
                    # print('----------------------------')
                    # print(source_link['url'])
                    image = ''
                    log_error(type='extract_image', page_url=source_link['url'], selector=source_link['image'],
                              data={}, error=PrintException(), source_id=str(source['_id']),
                              source_link_id=str(source_link['_id']), engine_instance_id=engine_instance_id, module='link_grabber')

                url_hash = create_md5(url)
                new_contents += 1

                if col_news.count_documents({'url_hash': url_hash}) == 0:
                    try:
                        col_news.insert_one({
                            'source_id': str(source['_id']),
                            'link_grabber_id': engine_instance_id,
                            'source_link_id': str(source_link['_id']),
                            'source_name': source['name'],
                            'create_date': datetime.now(),
                            'last_update': datetime.now(),
                            'url': url.encode('utf-8'),
                            'url_hash': url_hash,
                            'title': title.encode('utf-8'),
                            'summary': summary.encode('utf-8'),
                            'date': date,
                            'source_url': source_link['url'],
                            'status': 'summary',
                            'image': image,
                            'text_selector': source_link['text'],
                            'category_id': source_link['category_id'] if 'category_id' in source_link else '',
                            'text': '',
                            'html': '',
                        })
                    except Exception as e:
                        PrintException()
    except:
        PrintException()
        log_error(type='read_url', page_url=source_link['url'], selector='', data={}, error=PrintException(),
                  source_id=str(source['_id']), source_link_id=str(source_link['_id']),
                  engine_instance_id=engine_instance_id, module='link_grabber')


def worker():
    while True:
        item = q.get()
        do_work(item)
        q.task_done()


def run():
    # print('thread_count')
    # print(thread_count)
    for i in range(thread_count):
    # for i in range(10):
        t = threading.Thread(target=worker)
        t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
        t.start()
    if source_id == '':
        sources = col_sources.find({"enabled" : True})
    else:
        sources = col_sources.find({"_id": ObjectId(source_id)})
    # print('sources.count()')
    # print(sources.count())
    for source in sources:
        # print(1)
        for source_link in col_source_links.find({'source_id': str(source['_id'])}):
            # print(1)
            q.put({'source_link': source_link, 'source': source})
        # break
    q.join()


# def log_error(type, page_url, selector, data, error, source_id, source_link_id, engine_instance_id):
start = datetime.now()
engine_instance_id = str(col_engine_instances.insert_one({
    'type': 'link',
    'start_date': start,
    'duration': -1,
    'source_links': -1,
    'errors': -1,
    'new_contents': -1,
}).inserted_id)

error_count = 0
new_contents = 0
print(len(sys.argv))
# print(sys.argv[0])
source_id = ''
if len(sys.argv) > 1:
    print(sys.argv[1])
    source_id = sys.argv[1]
run()
duration = (datetime.now() - start).total_seconds()
print(col_engine_instances.update_one({'_id': ObjectId(engine_instance_id)}, {'$set': {
    'duration': duration,
    'errors': error_count,
    'source_links': link_count,
    'new_contents': new_contents
}}).raw_result)
print(duration)

