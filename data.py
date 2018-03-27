import os
from utils import get_sorted_imgs

pwd = os.path.abspath(os.curdir)
data = {
    # QQ动漫
    'username': "1042521247",
    'password': "qingdian171717",
    'comic_id': '632099',
    'use-appoint': True,
    'chapter-publish-time': '2018-03-24 14:00:00',
    'chapter_title': '叫什么好呢',
    'tips-chapter': os.path.join(pwd, 'images', '标题.jpg'),
    'pics': [f'{os.path.join(pwd,"images","章节",d)}' for d in get_sorted_imgs(os.path.join(pwd, 'images', '章节'))]
}
