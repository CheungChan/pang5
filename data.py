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
    'qq_chapter_title': '叫什么好呢',
    'qq_tips-chapter': os.path.join(pwd, 'images', '标题.jpg'),
    'qq_pics': [f'{os.path.join(pwd,"images","章节",d)}' for d in get_sorted_imgs(os.path.join(pwd, 'images', '章节'))],


    #网易
    'net_username':'18101038354',
    'net_password':'qingdian',
    #系列名
    'net-use-appoint':True,
    'net_series_title': '叫什么好呢',
    'net_title_text':'胖5号',
    'net_d':'2019-01-01',
    'net_h':'23',
    'net_m':'15',
    'net_image_pic':os.getcwd() + '/pic',


    #轻点
    'qingdian_username':'13311095487',
    "qingdian_password":'123456',
    'qingdian_series': '今天天气很好',
    'qingdian_chapter':os.getcwd() + '/pic/封面.jpg',
    'qingdian_title':'胖5号',
    'qingaidan_pic':os.getcwd() + '/pic',
}
