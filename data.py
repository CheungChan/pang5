import os
from utils import get_sorted_imgs

pwd = os.path.abspath(os.curdir)
data = {
    # QQ动漫
    'qq_username': "3389209527",
    'qq_password': "qingdian88",
    'qq_comic_id': '629518',
    'qq_use-appoint': True,
    'qq_chapter-publish-time': '2018-03-24 14:00:00',
    'qq_chapter_title': '喝醉的妹子竟然扯开了衣服',
    'qq_tips-chapter': os.path.join(pwd, 'images', '腾讯封面.jpg'),
    'qq_pics': [f'{os.path.join(pwd,"images","章节",d)}' for d in get_sorted_imgs(os.path.join(pwd, 'images', '章节'))],


    #网易
    'net_username':'qingdianmanhua@163.com',
    'net_password':'qingdian0908',
    #系列名
    'net-use-appoint':True,
    'net_series_title': '万物皆娘',
    'net_title_text':'喝醉的妹子竟然扯开了衣服',
    'net_d':'2018-04-02',
    'net_h':'18',
    'net_m':'15',
    'net_image_pic': [f'{os.path.join(pwd,"pic" ,d)}' for d in get_sorted_imgs(os.path.join(pwd, 'pic' ))],

    'qingdian_username':'13000002726',
    "qingdian_password":'qingdiancmc',
    'qingdian_series': '万物皆娘',
    'qingdian_chapter':os.path.join(pwd, 'series', '封面.jpg'),
    'qingdian_title':'喝醉的妹子竟然扯 开了衣服',
    'qingdian_pic':[f'{os.path.join(pwd,"pic" ,d)}' for d in get_sorted_imgs(os.path.join(pwd, 'pic' ))],
 }
