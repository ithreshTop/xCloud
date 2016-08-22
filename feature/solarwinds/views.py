__author__ = 'syx'
# coding: utf8

# 此模块未使用

from feature.sqlhelper import conn

cursor = conn.cursor()
cursor.execute('select * from Accounts')
for row in cursor:
    print('row = %r' % (row,))
    print row[0]

conn.close()