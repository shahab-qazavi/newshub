import sys
sys.path.append('/root/dev/newshub')
sys.path.append('/home/ehsan/dev/newshub')
from publics import db, PrintException
col_news = db()['news']
col_categories = db()['categories']
print(col_categories.count())
for item in col_categories.find():
    try:
        news_info = col_news.find({
            'category_id': str(item['_id']),
            'image': {'$ne': ''}
        }).sort('create_date', -1).limit(1)[0]
        print(col_categories.update_one({'_id': item['_id']}, {'$set': {'image': news_info['image']}}).raw_result)
        print('درسته')
    except:
        print('خرابه')
        print(item['name'])
        PrintException()


    # print(item)
    # print([0])


