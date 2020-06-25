
# from publics import db
# from datetime import datetime
# col_news = db()['news']
# start = datetime.now()
# for i in range(1000):
#     col_news.count({'url_hash': 'd60b312c93fdc526ac640cea47fcc66c'})
# print(datetime.now() - start)
#
# start = datetime.now()
# for i in range(1000):
#     col_news.find({'url_hash': 'd60b312c93fdc526ac640cea47fcc66c'}).limit(1)
# print(datetime.now() - start)
#
# start = datetime.now()
# for i in range(1000):
#     col_news.find_one({'url_hash': 'd60b312c93fdc526ac640cea47fcc66c'})
# print(datetime.now() - start)
#

from bs4 import BeautifulSoup
soup = BeautifulSoup('<script>a</script>baba<script>b</script>')
print([s.extract() for s in soup('script')])

# soup = BeautifulSoup(html) # create a new bs4 object from the html data loaded
for script in soup(["script", "style"]): # remove all javascript and stylesheet code
    script.extract()

print(soup)
