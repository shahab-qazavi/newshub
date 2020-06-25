import sys
sys.path.append('/root/dev/newshub')
from publics import db
col_sources = db()['sources']
for item in col_sources.find():
    if 'server1.onmiz.org' in item['logo']:
        print('yes')
        col_sources.update_one({'_id': item['_id']}, {'$set': {'logo': item['logo'].replace('server1', 'news')}})
    if '192.168.1.20' in item['logo']:
        print('yes')
        col_sources.update_one({'_id': item['_id']}, {'$set': {'logo': item['logo'].replace('192.168.1.20', 'news.onmiz.org')}})
    print(item['logo'])