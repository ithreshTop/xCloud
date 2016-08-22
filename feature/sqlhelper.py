# coding: utf-8

import pymssql

# 建立连接
conn = pymssql.connect(server='encndc2swm02',
                       port='1433',
                       user='sunyaxiong',
                       password='1qazxsw@',
                       database='NetPerfMon',
                       charset='UTF-8')
# 创建游标
cursor = conn.cursor()

# 执行sql
cursor.execute("select * from Accounts")

# 数据处理
for row in cursor:
    print('row = %r' % (row,))
    print row[0]

# 关闭连接
conn.close()

