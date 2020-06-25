# from publics import db
# col = db()['news']
# print(col.find_one()['url'])
# print(type(col.find_one()['url']))
# print(col.find_one()['url'].decode())
# print(type(col.find_one()['url'].decode()))
#
# if isinstance(col.find_one()['url'], bytes):
#     print('FUUUUUUUUUUUCK')


# import sys
# import traceback
#
# try:
#     1/0
# except:
#     exc_type, exc_value, exc_traceback = sys.exc_info()
#     lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
#     print(''.join('!! ' + line for line in lines))  # Log it or whatever here


# import logging
# import sys
#
# try:
#     a = 1 / 0
# except:
#     print('KOON')
#     print(sys.exc_info()[0])
#     print(sys.exc_info()[1])
#     print(sys.exc_info()[2])
#     print(sys.exc_info()[2].tb_lineno)
#     # traceback.print_exception()
#     print('KOON')
#     # logging.exception("message")
#
#
#
#
#
# etype, value, tb = sys.exc_info()
# ''.join(format_exception(etype, value, tb, limit))


