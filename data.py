import os
from utils import get_sorted_imgs

pwd = os.path.abspath(os.curdir)
data = {
    # QQ动漫
    'qq_username': "1042521247",
    'qq_password': "qingdian171717",
    'qq_comic_id': '632099',
    'qq_use-appoint': True,
    'qq_chapter-publish-time': '2018-03-24 14:00:00',
    'qq_chapter_title': '喝醉的妹子竟然扯开了衣服',
    'qq_tips-chapter': os.path.join(pwd, 'images', '封面.jpg'),
    'qq_pics': [f'{os.path.join(pwd,"images","章节",d)}' for d in get_sorted_imgs(os.path.join(pwd, 'images', '章节'))],

    # 网易
    # 'net_username': 'qingdianmanhua@163.com',
    # 'net_password': 'qingdian0908',
    'net_username': '18101038354',
    'net_password': 'qingdian',
    'net-use-appoint': True,
    'net-login': 'mobile',
    'net_series_title': '万物皆娘',
    'net_title_text': '喝醉的妹子竟然扯开了衣服',
    'net_d': '2018-04-02',
    'net_h': '18',
    'net_m': '15',
    'net_image_pic': [f'{os.path.join(pwd,"images" ,"章节",d)}' for d in get_sorted_imgs(os.path.join(pwd, "images","章节"))],

    # 轻点
    # 'qingdian_username': '13000002726',
    # "qingdian_password": 'qingdiancmc',
    'qingdian_username': '13311095487',
    "qingdian_password": '123456',
    'qingdian_series': '万物皆娘',
    'qingdian_chapter': os.path.join(pwd, 'images', '封面.jpg'),
    'qingdian_title': '喝醉的妹子竟然扯 开了衣服',
    'qingdian_pic': [f'{os.path.join(pwd,"images","章节",d)}' for d in get_sorted_imgs(os.path.join(pwd,"images","章节"))],

    # 麦萌
    'maimeng_username': '18101038354',
    'maimeng_password': 'qingdian17',
    'maimeng_series': '为什么救赎',
    'maimeng_chapter': os.path.join(pwd, 'series', '封面.jpg'),
    'maimeng_title': '喝醉的妹子竟然扯 开了衣服',
    'maimeng_desp': '简介',
    'maimeng_comment':'无特殊要求',
    'maimeng_publish_time': '2019-10-10 10:17:17',
    'maimeng_pic': [f'{os.path.join(pwd,"pic" ,d)}' for d in get_sorted_imgs(os.path.join(pwd, 'pic'))],
}
