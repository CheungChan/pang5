from config import DATA_WORKS_NAME, DATA_WORKS_IMAGE, DATA_USERNAME, DATA_THIRD_ID, DATA_PLATFORM, DATA_PASSWORD, \
    DATA_IS_CLOCK, DATA_CHAPTER_NAME, DATA_CLOCK_PUBLISH_DATETIME, DATA_CHAPTER_IMAGE, DATA_LOGIN_TYPE

# pwd = os.path.abspath(os.curdir)
# data = {
#     # QQ动漫
#     'qq_username': "1042521247",
#     'qq_password': "qingdian171717",
#     'qq_comic_id': '632099',
#     'qq_use-appoint': True,
#     'qq_chapter-publish-time': '2018-03-24 14:00:00',
#     'qq_chapter_title': '喝醉的妹子竟然扯开了衣服',
#     'qq_tips-chapter': os.path.join(pwd, 'images', '封面.png'),
#     'qq_pics': [f'"{os.path.join(pwd,"images","章节",d)}"' for d in get_sorted_imgs(os.path.join(pwd, 'images', '章节'))],
#
#     # 网易
#     # 'net_username': 'qingdianmanhua@163.com',
#     # 'net_password': 'qingdian0908',
#     'net_username': '18101038354',
#     'net_password': 'qingdian',
#     'net-use-appoint': True,
#     'net-login': 'mobile',
#     'net_series_title': '为什么救赎',
#     'net_title_text': '喝醉的妹子竟然扯开了衣服',
#     'net_d': '2018-04-26',
#     'net_h': '18',
#     'net_m': '15',
#     'net_image_pic': [f'{os.path.join(pwd,"images" ,"章节",d)}' for d in
#                       get_sorted_imgs(os.path.join(pwd, "images", "章节"))],
#
#     # 轻点
#     # 'qingdian_username': '13000002726',
#     # "qingdian_password": 'qingdiancmc',
#     # 'qingdian_username': '13311095487',# 杨浩
#     # "qingdian_password": '12341234',
#     'qingdian_username': '13000002729',  # 轻点酱
#     "qingdian_password": 'qingdian321',
#     # 'qingdian_series': '杨浩测试 不要审核通过',
#     'qingdian_series': '轻点活动',
#     'qingdian_chapter': os.path.join(pwd, 'images', '封面.png'),
#     'qingdian_title': '喝醉的妹子竟然扯 开了衣服',
#     'qingdian_pic': [f'{os.path.join(pwd,"images","章节",d)}' for d in
#                      get_sorted_imgs(os.path.join(pwd, "images", "章节"))],
#
#     # 麦萌
#     'maimeng_username': '18101038354',
#     'maimeng_password': 'qingdian17',
#     'maimeng_series': '为什么救赎',
#     'maimeng_chapter': os.path.join(pwd, 'images', '封面.png'),
#     'maimeng_title': '喝醉的妹子竟然扯 开了衣服',
#     'maimeng_desp': '',
#     'maimeng_comment': '无特殊要求',
#     'maimeng_publish_time': '2019-10-10 10:17:17',
#     'maimeng_pic': [f'"{os.path.join(pwd,"images","章节",d)}"' for d in
#                     get_sorted_imgs(os.path.join(pwd, "images", "章节"))],
#
#     # 有妖气
#     'u17_username': '1042521247@qq.com',
#     'u17_password': 'qingdian17',
#     'u17_series_name': '为什么救赎',
#     'u17_chapter_name': '喝醉的妹子竟然扯 开了衣服',
#     'u17_comic_id': '171154',
#     'u17_chapter_images': os.path.join(pwd, 'images', '封面.png'),
#     'u17_pic': [f'"{os.path.join(pwd,"images","章节",d)}"' for d in get_sorted_imgs(os.path.join(pwd, "images", "章节"))],
# }

data = {
    DATA_PLATFORM: '',  # 平台
    DATA_LOGIN_TYPE: '',  # 登录类型
    DATA_USERNAME: '',  # 用户名
    DATA_PASSWORD: '',  # 密码
    DATA_WORKS_NAME: '',  # 作品名称
    DATA_CHAPTER_NAME: '',  # 章节名称
    DATA_THIRD_ID: '',  # 第三方平台id
    DATA_WORKS_IMAGE: '',  # 作品封面
    DATA_CHAPTER_IMAGE: '',  # 章节图片
    DATA_IS_CLOCK: '',  # 是否定时
    DATA_CLOCK_PUBLISH_DATETIME: '',  # 定时发布时间
}
