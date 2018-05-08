from sys import argv
from rabbit_pang5 import insert_rabbit

if len(argv) == 2:
    mysql_id = int(argv[1])
    insert_rabbit({'mysql_id': mysql_id})
else:
    print('请跟上mysql_id  int参数')
